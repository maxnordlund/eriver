import json, copy

if __name__ == "__main__":
  path = "starcraft2.json"
  with open(in_path, encoding="UTF-8") as fil:
    data = json.load(fil)
    out = copy.deepcopy(data)
    ratios = data.keys()
    for ratio in ratios:
      for name, region in data[ratio]:
        for subratio in ratios:
          if subratio != ratio:
            subregion = data[subratio][name]
            if region["type"] == "rect":
              pass
            elif region["type"] == "circle":
              pass
  with open(out_path, "w", encoding="UTF-8") as fil:
    json.dump(out_path, fil, indent=4, separators=(',', ': '))
