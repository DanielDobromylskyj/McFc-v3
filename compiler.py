import os
import shutil


class moddedVanillaPack:
    def __init__(self, name):
        self.packVersion = 36
        self.requiredSnapshot = "24w12a"

        self.name = name
        self.__segments = []

    def add_segment(self, segment):
        self.__segments.append(segment)

    def compile(self, to):
        if os.path.exists("data"):
            shutil.rmtree("data")

        os.mkdir("data")

        if os.path.exists("resourcePack"):
            shutil.rmtree("resourcePack")

        os.mkdir("resourcePack")

        for subSegment in self.__segments:
            subSegment.compile(self)


craftingRecipiePatternCharacters = "#@$%&+-*/"


class craftingRecipie:
    def __init__(self, itemObject, recipie):
        self.item = itemObject
        self.recipie = recipie

        self.modPack = None

    def createPattern(self):
        uniqueItems = {}
        pattern = [" " for i in range((self.recipie["gridSize"] if "gridSize" in self.recipie else 3) ** 2)]

        for i, subItem in enumerate(self.recipie["recipie"]):
            if (subItem is not None) and (subItem not in uniqueItems.values()):
                itemKey = subItem[0] if subItem[0] not in uniqueItems.keys() else craftingRecipiePatternCharacters[
                    len(uniqueItems)]
                uniqueItems[itemKey] = subItem
                pattern[i] = itemKey

        return self.formatPattern(pattern), self.formatKey(uniqueItems)

    def formatPattern(self, pattern):
        newPattern = []
        gridSize = self.recipie["gridSize"] if "gridSize" in self.recipie else 3
        for i in range(0, len(pattern), gridSize):
            newPattern.append(''.join(pattern[i:i + gridSize]))
        return newPattern

    def formatKey(self, key):
        return {
            subKey: f'"item": ""'
            for subKey in key.keys()
        }

    def createJson(self, pattern, patternKey, shaped):
        if self.modPack is None:
            raise Exception("Mod-pack Not initialised!")

        if shaped:
            return str({
                "type": "minecraft:crafting_shaped",
                "pattern": pattern,
                "key": patternKey,
                "result": self.item.getItemJson()
            })

        return str({
            "type": "minecraft:crafting_shaped",
            "ingredients": [],
            "result": self.item.getItemJson()
        })

    def compile(self, modPack):
        self.modPack = modPack

        if os.path.exists("data/customRecipies/recipes") is False:  # POSSIBLE FAULT - spelling of "recipes" may change
            os.mkdir("data/customRecipies")
            os.mkdir("data/customRecipies/recipes")

        if "name" not in self.item.nbt:
            raise Exception("Cannot Create Recipie - Item Does Not Have A Name. NBT:", self.item.nbt)

        if "recipie" not in self.recipie:
            raise Exception(f"Cannot Create Recipie - No Recipie Given For {self.item.nbt['name']}")

        pattern, patternKey = self.createPattern()
        shaped = self.recipie.get("exactLayout") is not False

        jsonData = self.createJson(pattern, patternKey, shaped)

        with open(f"data/customRecipies/recipes/{self.item.nbt['name']}.json", "w") as f:
            f.write(jsonData)


class item:
    def __init__(self, customNBT):
        self.modPack = None
        self.nbt = customNBT

    def getItemJson(self):  # fixme / todo
        if self.modPack is None:
            raise Exception("Mod-pack not initialised!")

        if "name" not in self.nbt:
            raise Exception("Cannot Create Item - Item Does Not Have A Name. NBT:", self.nbt)

        if (baseName := self.nbt.get("baseItem")) is not None:
            if "texture" in self.nbt:
                return {
                    "item": f"minecraft:{baseName}",
                    "custom_data": {"customModelID": self.nbt["texture"].id}  # ???
                }
            else:
                return {
                    "item": f"minecraft:{baseName}"
                }

        else:
            return {
                "item": self.modPack.name + ":" + self.nbt["name"]
            }

    def addCraftingRecipie(self, recipie):
        self.nbt["recipie"] = craftingRecipie(self, recipie)

    def compile(self, modPack):
        self.modPack = modPack

        if "recipie" in self.nbt:
            self.nbt["recipie"].compile(modPack)


numberOfMcFcTexturesInUse = 1


class texture:
    def __init__(self, path):
        self.path = path

        global numberOfMcFcTexturesInUse
        self.id = str(numberOfMcFcTexturesInUse).zfill(6)
        numberOfMcFcTexturesInUse += 1

    def compile(self, modPack):  # No Compile Function ???
        pass


if __name__ == "__main__":
    # Create a minecraft datapack
    modPack = moddedVanillaPack('VanPlus')

    customItem = item({
        "name": "ruby",
        "baseItem": "emerald",
        "texture": texture("demos/ruby/ruby.png")
    })

    customItem.addCraftingRecipie({
        "recipie": ["diamond", "redstone_dust"],
        "gridSize": 2,
        "exactLayout": False
    })

    modPack.add_segment(customItem)

    modPack.compile(to="demos/ruby/")
