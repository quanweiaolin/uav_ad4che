import cv2 as cv
import numpy as np


def harris_corner_detect(
    img_gray, 
    mask=None,
    blockSize=2,    # Harris检测的邻域大小（默认2）
    ksize=3,        # Sobel算子核大小（默认3，必须为奇数）
    k=0.04,         # Harris响应值计算参数（默认0.04，范围0.04~0.06）
    response_thresh=0.07  # 角点响应值阈值（默认0.01，越小检测越多角点）case8:0.01  case7:0.07
):
    """
    极简版Harris角点检测（仅保留核心逻辑，无任何额外优化）
    参数：
        img_gray: 输入灰度图像（np.ndarray，单通道）
        blockSize: Harris检测的邻域大小
        ksize: Sobel算子核大小（奇数）
        k: Harris响应值计算参数
        response_thresh: 角点筛选阈值（响应值 > thresh*max_response 才视为角点）
    返回：
        kp_list: 检测到的角点列表（cv2.KeyPoint对象）
    """
    # 1. 核心：计算Harris响应值（float32格式）
    dst = cv.cornerHarris(img_gray, blockSize, ksize, k)
    
    # 2. 筛选高响应值角点（仅保留超过阈值的角点）
    # 阈值 = 响应值最大值 * 比例系数
    thresh = response_thresh * dst.max()
    # 找到所有满足条件的角点坐标（格式：(y, x)）
    corners_yx = np.argwhere(dst > thresh)
    
    # 3. 转换为cv2.KeyPoint格式（适配后续描述符提取）
    kp_list = []
    for y, x in corners_yx:
        # KeyPoint参数：x坐标、y坐标、邻域大小（设为31，兼容ORB默认值）、角度（-1表示无方向）
        kp = cv.KeyPoint(
            x=float(x),
            y=float(y),
            size=31,  # 仅为适配后续ORB描述符，无实际Harris尺度含义
            angle=-1  # Harris无方向信息，固定设为-1
        )
        kp_list.append(kp)
    
    # 掩码处理
    if mask is not None:
        filtered_kp = []
        for kp in kp_list:
            x, y = int(kp.pt[0]), int(kp.pt[1])
            # 检查坐标是否在图像范围内
            if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1]:
                if mask[y, x] == 255:
                    filtered_kp.append(kp)
        return filtered_kp
    else:
        return kp_list

def image_mask(mask_img_path, width, height):
    """根据图片获取掩码：读取黑白掩码jpg图片，提取白色区域作为稳定区域的二值掩码"""
    mask_img = cv.imread(mask_img_path)
    if mask_img is None:
        print("警告：未传入掩码，将使用全图进行稳定化")
        mask_img = np.ones((height, width), dtype=np.uint8) * 255  # 全图掩码
    
    # 转换为灰度图
    gray_mask = cv.cvtColor(mask_img, cv.COLOR_BGR2GRAY)
    
    # 二值化：白色区域（灰度值接近255）设为255，其他设为0（确保只有白色区域有效）
    _, binary_mask = cv.threshold(gray_mask, 240, 255, cv.THRESH_BINARY)
    mask = binary_mask.astype(np.uint8)
    
    return mask

def downsample_frame(frame, downsample_ratio):
    """降分辨率函数"""
    if downsample_ratio == 1.0:
        return frame.copy()
    h, w = frame.shape[:2]
    new_w = int(w * downsample_ratio)
    new_h = int(h * downsample_ratio)
    down_frame = cv.resize(frame, (new_w, new_h), interpolation=cv.INTER_AREA)
    return down_frame

def match_features(des1, des2, matcher, filter_ratio):
    """特征匹配（默认BF方案，比率测试0.9）"""
    matches = matcher.knnMatch(des1, des2, k=2)
    good_matches = []
    for m, n in matches:
        if m.distance < filter_ratio * n.distance:
            good_matches.append(m)
    return good_matches
    
def compute_transform(kp1, kp2, matches, ransac_method, ransac_reproj_thresh, ransac_max_iter, ransac_confidence):
    """计算变换矩阵（固定透视变换+MAGSAC++），新增返回内点数量"""
    inliers_count = 0  # 初始化内点数量
    if len(matches) < 4:
        return np.eye(3), inliers_count
    
    pts1 = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    pts2 = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    H, inlier_mask = cv.findHomography(
        pts2, pts1,
        method=ransac_method,
        ransacReprojThreshold=ransac_reproj_thresh,
        maxIters=ransac_max_iter,
        confidence=ransac_confidence
    )
    
    # 统计内点数量
    if inlier_mask is not None:
        inliers_count = np.count_nonzero(inlier_mask)
    
    H = H if H is not None else np.eye(3)
    return H, inliers_count

def scale_homography_matrix(H, downsample_ratio):
    """缩放透视变换矩阵到原分辨率"""
    if downsample_ratio == 1.0:
        return H
    
    # 缩放矩阵：先放大坐标，再应用变换，再缩小（逆过程）
    # 构造缩放矩阵
    scale = 1.0 / downsample_ratio
    # 缩放矩阵 M = [[scale, 0, 0], [0, scale, 0], [0, 0, 1]]
    M_scale = np.array([
        [scale, 0, 0],
        [0, scale, 0],
        [0, 0, 1]
    ], dtype=np.float32)
    # 逆缩放矩阵
    M_inv_scale = np.array([
        [downsample_ratio, 0, 0],
        [0, downsample_ratio, 0],
        [0, 0, 1]
    ], dtype=np.float32)
    
    # 变换矩阵组合：M_scale * H * M_inv_scale
    H_scaled = M_scale @ H @ M_inv_scale
    return H_scaled

def analyze_homography(H):
    # 分解平移分量
    tx, ty = H[0, 2], H[1, 2]
    
    # 分解旋转和缩放分量（通过前两列的子矩阵）
    R = H[:2, :2]
    # 计算缩放因子（奇异值分解）
    scales = np.linalg.svd(R, compute_uv=False)
    scale_x, scale_y = scales[0], scales[1]
    
    # 透视分量（最后一行前两个元素）
    perspective_x, perspective_y = H[2, 0], H[2, 1]
    return tx, ty, scale_x, scale_y, perspective_x, perspective_y
    # print(f"平移: tx={tx:.2f}, ty={ty:.2f}")
    # print(f"缩放: sx={scale_x:.2f}, sy={scale_y:.2f}")
    # print(f"透视分量: px={perspective_x:.4f}, py={perspective_y:.4f}")
def resize_frame(frame, target_resolution):
    mapping = {
        "4k": (3840, 2160),
        "2k": (2560, 1440),
        "1080p": (1920, 1080)
    }
    if target_resolution in mapping:
        return cv.resize(frame, mapping[target_resolution])

def optical_lk(frame_gray,prev_frame_gray,feature_params):

    prev_corners = cv.goodFeaturesToTrack(prev_frame_gray, mask=None, **feature_params)


    next_corners, st, err = cv.calcOpticalFlowPyrLK(prev_frame_gray, frame_gray, prev_corners, None)

    # 筛选匹配良好的点
    good_new = next_corners[st == 1]
    good_old = prev_corners[st == 1]


    # transform, _ = cv.estimateAffinePartial2D(good_new, good_old, method=cv.RANSAC)
    transform,mask = cv.findHomography(good_new, good_old, cv.RANSAC, 5.0)
    # 应用仿射变换进行对齐
    return transform

def preprocess_frame(frame, downsample_ratio):
    """优化：帧预处理（先降分辨率，再转灰度）"""
    frame_down = downsample_frame(frame, downsample_ratio)
    gray = cv.cvtColor(frame_down, cv.COLOR_BGR2GRAY)
    return gray

# v2 新增
def read_mask(mask_img_path):
    """
    读取黑白掩码图片，提取白色区域作为稳定区域的二值掩码
    :param mask_image_path: 掩码图片（jpg格式）的路径
    :return: np.uint8类型的二值掩码（白色区域为255，黑色区域为0）
    """
    # 读取掩码图片
    mask_img = cv.imread(mask_img_path)
    if mask_img is None:
        raise FileNotFoundError(f"无法读取掩码图片：{mask_img_path}")
    
    # 转换为灰度图
    gray_mask = cv.cvtColor(mask_img, cv.COLOR_BGR2GRAY)
    
    # 二值化：白色区域（灰度值接近255）设为255，其他设为0（确保只有白色区域有效）
    _, binary_mask = cv.threshold(gray_mask, 240, 255, cv.THRESH_BINARY)
    
    # 确保输出为np.uint8类型
    return binary_mask.astype(np.uint8)

def apply_homography_to_video(input_video_path, output_video_path, H):
    """
    将单应性矩阵应用到视频的每一帧
    
    参数:
        input_video_path: 输入视频路径
        output_video_path: 输出视频路径
        H: 单应性矩阵
    """
    cap = cv.VideoCapture(input_video_path)
    if not cap.isOpened():
        print(f"无法打开输入视频: {input_video_path}")
        return
    
    # 获取视频属性
    fps = cap.get(cv.CAP_PROP_FPS)
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    
    # 创建视频写入器
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    out = cv.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        print(f"无法创建输出视频: {output_video_path}")
        cap.release()
        return
    
    frame_count = 0
    print(f"开始处理视频: {input_video_path}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 应用单应性矩阵变换
        if H is not None:
            aligned_frame = cv.warpPerspective(frame, H, (width, height))
        else:
            aligned_frame = frame  # 如果H为None，使用原帧
        
        # 写入输出视频
        out.write(aligned_frame)
        frame_count += 1
        
        if frame_count % 30 == 0:  # 每30帧打印一次进度
            print(f"处理进度: {frame_count}/{total_frames} 帧")
    
    cap.release()
    out.release()
    print(f"视频处理完成: {output_video_path}")
    print(f"总处理帧数: {frame_count}")

def compute_homography(base_image, target_image):
    """
    计算从目标图像到基准图像的单应性矩阵
    
    参数:
        base_image: 基准图像
        target_image: 需要对齐的目标图像
    
    返回:
        H: 单应性矩阵
        good_matches: 良好匹配点数量
    """
    # 初始化特征检测器 - 使用AKAZE
    feature_detector = cv.AKAZE_create()
    
    # 转换为灰度图
    base_gray = cv.cvtColor(base_image, cv.COLOR_BGR2GRAY)
    target_gray = cv.cvtColor(target_image, cv.COLOR_BGR2GRAY)
    
    # 检测基准图像的特征点和描述符
    kp1, des1 = feature_detector.detectAndCompute(base_gray, None)
    kp2, des2 = feature_detector.detectAndCompute(target_gray, None)
    
    # 使用BFMatcher进行特征匹配
    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    
    # 按距离排序，取前80%的良好匹配
    matches = sorted(matches, key=lambda x: x.distance)
    num_good_matches = int(len(matches) * 0.8)
    good_matches = matches[:num_good_matches]
    
    H = None
    # 至少需要4个匹配点才能计算单应性矩阵
    if len(good_matches) >= 4:
        # 提取匹配点的坐标
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        # 使用RANSAC算法计算单应性矩阵
        H, mask = cv.findHomography(dst_pts, src_pts, cv.RANSAC, 5.0)
        print(f"成功计算单应性矩阵，良好匹配点: {len(good_matches)}")
    else:
        print(f"计算单应性矩阵失败，匹配点不足。找到 {len(good_matches)} 个匹配点，需要至少4个")
    
    return H, len(good_matches)

def f1(kp, des, mask=None, use_mask=True, use_target_length=True, target_length=8000):
    """高效筛选特征点和描述符"""
    if not kp or des is None:
        return [], None
    if use_mask and mask is None:
        raise ValueError("当use_mask=True时，必须传入有效的mask参数")
    
    kp_coords = np.array([(p.pt[0], p.pt[1]) for p in kp], dtype=np.float32)
    kp_coords_int = np.round(kp_coords).astype(np.int32)
    
    if use_mask:
        height, width = mask.shape[:2]
    else:
        height, width = int(np.max(kp_coords[:, 1])) + 1, int(np.max(kp_coords[:, 0])) + 1
        
    valid_boundary = (kp_coords_int[:, 0] >= 0) & (kp_coords_int[:, 0] < width) & \
                     (kp_coords_int[:, 1] >= 0) & (kp_coords_int[:, 1] < height)
    valid_indices = np.where(valid_boundary)[0]
    
    if use_mask:
        valid_coords = kp_coords_int[valid_boundary]
        valid_mask = mask[valid_coords[:, 1], valid_coords[:, 0]] == 255
        final_indices = valid_indices[valid_mask]
    else:
        final_indices = valid_indices
    
    n = final_indices.shape[0]
    if n == 0:
        return [], None
        
    if target_length >= n and use_target_length:
        selected_indices = final_indices
    else:
        selected_indices = final_indices[np.linspace(0, n - 1, target_length, dtype=int)]
        
    filtered_kp = [kp[i] for i in selected_indices]
    filtered_des = des[selected_indices] if len(selected_indices) > 0 else None
    
    return filtered_kp, filtered_des

def match_perspective(feature_detector, current_frame,ref_frame, stable_mask):
    """
    current_frame: 是需要进行透视变化的当前帧
    ref_frame: 参考帧
    stable_mask: 稳定区域掩码
    return： H: 计算得到的单应性矩阵
          aligned_frame: 透视变换后的对齐帧
          current_des: 当前帧的描述符
          current_kp: 当前帧的关键点
    """
    current_gray = cv.cvtColor(current_frame, cv.COLOR_BGR2GRAY)
    ref_gray = cv.cvtColor(ref_frame, cv.COLOR_BGR2GRAY)
    current_kp_raw, current_des_raw = feature_detector.detectAndCompute(current_gray, None)
    current_kp, current_des = f1(current_kp_raw, current_des_raw, stable_mask)  # 使用图片掩码

    ref_kp_raw, ref_des_raw = feature_detector.detectAndCompute(ref_gray, None)
    ref_kp, ref_des = f1(ref_kp_raw, ref_des_raw, stable_mask)  # 使用图片掩码
    width , height = current_frame.shape[1], current_frame.shape[0]
    aligned_frame = current_frame

    
    if ref_des is not None and current_des is not None:
        bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=False)
        matches = sorted(bf.match(ref_des, current_des), key=lambda x: x.distance)
        good_matches = matches[:int(len(matches)*0.8)]
        
        if len(good_matches) >= 4:
            src_pts = np.float32([ref_kp[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([current_kp[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            # 【修改】获取RANSAC掩码，计算内点数量
            H, mask = cv.findHomography(dst_pts, src_pts, cv.RANSAC, 5.0)
            if H is not None:
                aligned_frame = cv.warpPerspective(current_frame, H, (width, height))
                # 【新增3】统计内点数量（mask中1表示内点）
                return H, aligned_frame,current_des,current_kp
    return None, aligned_frame,current_des,current_kp