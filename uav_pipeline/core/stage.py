class Stage:
    name = "base_stage"

    def run(self, ctx):
        raise NotImplementedError("Stage must implement run(ctx)")