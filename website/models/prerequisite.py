class Prerequisite:
    module_id: str
    requires_module_id: str

    def __init__(self, module_id: str, requires_module_id: str):
        self.module_id = module_id
        self.requires_module_id = requires_module_id