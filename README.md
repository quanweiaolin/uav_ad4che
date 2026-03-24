# UAV AD4CHE Pipeline

A development repository for data processing, analysis, and scenario mining based on the **AD4CHE aerial traffic dataset**.

This project provides tools and pipelines for processing UAV traffic videos, generating trajectory data, and extracting driving scenarios for autonomous driving research.

## Overview

The **AD4CHE Dataset** is a UAV-based traffic dataset collected over Chinese highways and expressways, focusing on **congestion scenarios and vehicle interaction behaviors**. The dataset includes several hours of aerial recordings and thousands of vehicle trajectories, providing valuable data for studying human driving behavior and scenario-based testing of autonomous driving systems.

This repository extends the original dataset by providing:

* UAV video processing pipelines
* Detection and tracking modules
* Scenario extraction tools
* Data management utilities
* Dataset development utilities for future extensions****

The goal is to build a **reproducible data pipeline for aerial traffic analysis and autonomous driving research**.

## Repository Structure

```
uav_ad4che
│
├─ stages/
│  ├─ extract_frames/      # Extract frames from UAV videos
│  ├─ detection/           # Vehicle detection models
│  ├─ tracking/            # Multi-object tracking
│  └─ postprocess/         # Trajectory filtering and smoothing
│
├─ scripts/                # Utility scripts
│
├─ data/                   # Local dataset storage (not tracked by Git)
│
├─ configs/                # Pipeline configuration
│
└─ docs/                   # Documentation
```


## Pipeline

The UAV AD4CHE pipeline processes aerial traffic data through the following steps:

### 1. Video Ingestion

* Import UAV recordings
* Extract frames for downstream processing

### 2. Vehicle Detection

* Apply object detection models to identify vehicles in each frame

### 3. Multi-Object Tracking

* Associate vehicle detections across frames
* Generate consistent vehicle trajectories

### 4. Trajectory Post-processing

* Remove noise and fragmented tracks
* Interpolate missing detections

### 5. Scenario Mining

* Extract traffic interaction scenarios such as:
* cut-in
* lane change
* congestion interactions
* merging events


## Dataset

The dataset can be obtained from the official AD4CHE project:

Dataset website:

[https://www.zyt.com/zh/development](https://https://www.zyt.com/zh/development)

The dataset contains UAV recordings of congested highways and expressways, enabling analysis of driver behavior and interaction patterns.

- Dataset duration: 5.12 hours
- Total vehicles: 53,761
- Lane changes: 16,099
- Cut-in events: 3,331
- Recording platform: UAV aerial platform
- Scenarios: congested highway & expressway


## Development

The project is under active development and aims to support:

* scalable UAV dataset processing
* scenario-based autonomous driving evaluation
* integration with simulation platforms
* machine learning dataset generation


## Citation

If you use the AD4CHE dataset or this repository in your research, please cite the following paper:

> Zhang, Y., Quan, W., Gao, Y., Li, P., Kuang, H., Zhao, F., Du, X., Yu, R., Wang, L., Qiao, J.
> Aerial Dataset for China Congested Highway & Expressway and its Potential Applications in Automated Driving Systems Development.
> TechRxiv, 2022.
> https://doi.org/10.36227/techrxiv.20236698.v1
