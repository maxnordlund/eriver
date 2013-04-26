import json, copy

def ratio_of(string):
  return [int(n) for n in string.split(":")]

def adjust(primary, secondary, subprimary, subsecondary):
  scale = primary / subprimary
  normal = secondary / (subsecondary * scale)
  return normal, (normal - 1) / 2

if __name__ == "__main__":
  in_path  = "starcraft2.json"
  out_path = "starcraft2.gen.json"
  with open(in_path, encoding="UTF-8") as fil:
    data = json.load(fil)
  out = copy.deepcopy(data)
  ratios = data.keys()
  for ratio in ratios:
    for name, region in data[ratio]:
      for subratio in ratios:
        key = "%s_%s" % ratio, subratio
        if subratio != ratio:
          if key not in out:
            out[key] = dict()
          subregion = data[subratio][name]
          width, height = ratio_of(ratio)
          subwidth, subheight = ratio_of(subratio)
          if region["type"] == "rect":
            if width/height > subwidth/subheight:
              width_scale, delta_width = adjust(height, width, subheight, subwidth)
              height_scale, delta_height = 1, 0
            else:
              height_scale, delta_height = adjust(width, height, subwidth, subheight)
              width_scale, delta_width = 1, 0

            out[key][name] = {
              "type": "rect"
              "top": subregion["top"] * height_scale + delta_height,
              "right": subregion["right"] * width_scale + delta_width,
              "bottom": subregion["bottom"] * height_scale + delta_height,
              "left": subregion["left"] * width_scale + delta_width
            }
          elif region["type"] == "circle":
            out[key][name] = copy.deepcopy(subregion)
  with open(out_path, "w", encoding="UTF-8") as fil:
    json.dump(out_path, fil, indent=4, separators=(',', ': '))
