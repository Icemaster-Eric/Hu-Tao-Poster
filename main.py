from PIL import Image, ImageDraw, ImageFont
import math

# hu tao's butterfly :)
butterfly_mask_img = Image.open("butterfly_mask.png").convert("RGBA")
butterfly_mask_img = butterfly_mask_img.crop(butterfly_mask_img.getbbox())
butterfly_mask_img = butterfly_mask_img.resize((100, 100), resample=Image.Resampling.LANCZOS)
butterfly_mask_img = butterfly_mask_img.rotate(60, resample=Image.Resampling.BICUBIC, expand=True)

mask_img = Image.open("mask.png").convert("RGBA")
mask_img.paste(butterfly_mask_img, (200, 692), butterfly_mask_img)
# mask_img = mask_img.crop( # should it be a square?
#     (0, mask_img.height-mask_img.width, mask_img.width, mask_img.height)
# )
mask_alpha = mask_img.split()[-1]

target_img = Image.open("target.png").convert("RGBA")
target_width, target_height = target_img.size

# scale target image to cover the mask size
scale = 1.04
new_width = int(target_width * scale)
new_height = int(target_height * scale)
resized_target = target_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

# crop the resized target to the mask size
left = (new_width - mask_img.width) // 2 + 50
upper = (new_height - mask_img.height) // 2
right = left + mask_img.width
lower = upper + mask_img.height
cropped_target = resized_target.crop((left, new_height-mask_img.height, right, new_height))

# apply mask alpha as binary silhouette
r, g, b, a = cropped_target.split()
silhouette_img = Image.merge("RGBA", (r, g, b, mask_alpha))

# create background image
base_img = Image.open("background.png").convert("RGBA")
base_img = base_img.resize(
    (round(base_img.width * 1.8), round(base_img.height * 1.8)),
    Image.Resampling.LANCZOS
).crop((0, 0, silhouette_img.width, silhouette_img.height)) # crop to correct height of silhouette

# the drawer thing
draw = ImageDraw.Draw(base_img)

# nudge the left butterfly to the left a bit more and make it smaller
left_butterfly_img = base_img.crop((50, 400, 290, 610)).resize(
    (120, 115), Image.Resampling.LANCZOS
)
draw.rectangle(((50, 400), (290, 610)), fill=base_img.getpixel((0, 0)))
base_img.paste(left_butterfly_img, (40, 430))
# nudge the right cloud to the right a bit more and make it smaller too
right_cloud_img = base_img.crop((720, 650, 1280, 1000)).resize(
    (392, 245), Image.Resampling.LANCZOS
)
draw.rectangle(((720, 650), (1280, 1000)), fill=base_img.getpixel((0, 0)))
base_img.paste(right_cloud_img, (910, 670))
# hide the butterfly on the bottom left
draw.rectangle(((200, 1270), (270, 1340)), fill=base_img.getpixel((0, 0)))

# color thingy to test out black background
def color_dist(c1, c2):
    return (c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2

px = base_img.load()
bg_color = base_img.getpixel((0, 0))
for y in range(base_img.height):
    for x in range(base_img.width):
        dist = color_dist(px[x, y], bg_color) # type: ignore
        
        if dist <= 500: # type: ignore
            norm = min(dist / 500, 1.0)
            dim_factor = math.exp(-2 * (1 - norm))
            r, g, b, a = px[x, y] # type: ignore
            # change this so that the dimming amount is proportional to how close it is to the bg_color
            px[x, y] = ( # type: ignore
                int(max(0, min(255, r * dim_factor))),
                int(max(0, min(255, g * dim_factor))),
                int(max(0, min(255, g * dim_factor))),
                a
            )
        else:
            r, g, b, a = px[x, y] # type: ignore
            # Shift colors with clamping to 0–255
            r = max(0, min(255, r-30))
            b = max(0, min(255, b+10))
            px[x, y] = (r, g, b, a) # type: ignore

# text shadow
font = ImageFont.truetype("HanyiSentyPagoda Regular.ttf", size=186)
draw.text((980, 220), "胡", (212,61,71,50), font)
draw.text((980, 410), "桃", (212,61,71,50), font)
# text
font = ImageFont.truetype("HanyiSentyPagoda Regular.ttf", size=180)
draw.text((980, 220), "胡", (212,61,71), font)
draw.text((980, 410), "桃", (212,61,71), font)

# silhouette shadow
shadow_img = silhouette_img.resize(
    (silhouette_img.width + 20, silhouette_img.height + 20), resample=Image.Resampling.LANCZOS
)
shadow_color = (138, 28, 28)
blend_ratio = 1
px = shadow_img.load()
for y in range(shadow_img.height):
    for x in range(shadow_img.width):
        r, g, b, a = px[x, y]  # type: ignore
        if a > 0:
            # color blending for shadow to give sort of a glassy feel?
            nr = int(r * (1 - blend_ratio) + shadow_color[0] * blend_ratio)
            ng = int(g * (1 - blend_ratio) + shadow_color[1] * blend_ratio)
            nb = int(b * (1 - blend_ratio) + shadow_color[2] * blend_ratio)
            px[x, y] = (nr, ng, nb, int(a * 0.8))  # type: ignore
# add shadow
base_img.paste(shadow_img, (0, 0), shadow_img)

# add silhouette
base_img.paste(silhouette_img, (0, 0), silhouette_img)

# save result
base_img.save("result.png")
base_img.show("Hu Tao Poster")
