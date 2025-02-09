import uuid
from typing import Optional, Union, List
from maesterd.models.campaign import CampaignSetting

from maesterd.models.character import PC


class CampaignSession:

    id = uuid.uuid4()
    setting: Optional[CampaignSetting] = None
    model = None
    pcs = []

    @classmethod
    def add_pcs(cls, pc: Union[PC, List[PC]]):
        if isinstance(pc, list):
            cls.pcs.extend(p for p in pc if p not in cls.pcs)  # Avoid duplicates
        else:
            if pc not in cls.pcs:
                cls.pcs.append(pc)

    @classmethod
    def remove_pcs(cls, pc: Union[PC, List[PC]]):
        if isinstance(pc, list):
            cls.pcs = [p for p in cls.pcs if p not in pc]
        else:
            if pc in cls.pcs:
                cls.pcs.remove(pc)

    @classmethod
    def add_campaign_setting(cls, setting: CampaignSetting):
        """
        Add a campaign setting to the session.

        Args:
            setting (CampaignSetting): The campaign setting to add.
        """
        cls.setting = setting

    @classmethod
    def get_pc_state(cls, name: str):
        return list(filter(lambda x: x.get('character', {}).get('name') == name, cls.pcs))[0]['state']

    @classmethod
    def get_pc_names(cls):
        return list(map(lambda x: x.get('character', {}).get('name'), cls.pcs))
