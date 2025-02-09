from dataclasses import dataclass, field


@dataclass
class CampaignSetting:
    name: str = field(metadata={"description": "Name of the campaign"})
    setting: str = field(metadata={"description": "Setting or world where the campaign takes place"})
    goal: str = field(metadata={"description": "The main goal or objective of the campaign"})
