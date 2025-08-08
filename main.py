from PIL import Image, ImageDraw, ImageFont

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

# add text
font = ImageFont.truetype("HanyiSentyPagoda Regular.ttf", size=190)
draw.text((950, 200), "胡", (255, 255, 255, 255), font)
draw.text((950, 400), "桃", (255, 255, 255, 255), font)

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
base_img.paste(right_cloud_img, (910, 650))
# make the right butterfly a bit smaller
right_butterfly_img = base_img.crop((950, 1050, 1280, 1300)).resize(
    (231, 175), Image.Resampling.LANCZOS
)
draw.rectangle(((950, 1050), (1280, 1300)), fill=base_img.getpixel((0, 0)))
base_img.paste(right_butterfly_img, (1050, 1180))

# add silhouette
base_img.paste(silhouette_img, (0, 0), silhouette_img)
# save result
base_img.save("result.png")
base_img.show("Hu Tao Poster")
