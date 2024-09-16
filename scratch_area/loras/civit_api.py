import requests

def search_for_lora(query: str, baseModel: str, page: int = 1):
    as_data = {
        "types": "LORA",
        "sort": "Highest Rated",
        "limit": 20,
        "page": page,
        "nsfw": False,
        "query": query,
        "baseModels": baseModel,
    }
    url = "https://civitai.com/api/v1/models"
    v = requests.get(url, params=as_data)
    with open("tmp.json", "wb") as f:
        f.write(v.content)


class LoRA:
    name: str
    strength: float
    clip_strength: float
    inject_trigger = "any"
    is_version: bool
    civit_id: int

    def to_horde(self):
        return {
            "name": str(self.civit_id) ,
            "model": self.strength,
            "clip": self.clip_strength,
            "inject_trigger": self.inject_trigger,
            "is_version": self.is_version,
        }
    @classmethod
    def from_civit(cls,val: dict):
        k=cls()
        k.name=val.get("name","Invalid LoRA")
        k.strength=1
        k.clip_strength=1
        k.is_version=False
        pass

search_for_lora("Artists", "Pony", 1)
