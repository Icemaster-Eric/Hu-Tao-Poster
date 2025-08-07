from PIL import Image

butterfly_mask_img = Image.open("butterfly_mask.png").convert("RGBA")
butterfly_mask_img = butterfly_mask_img.crop(butterfly_mask_img.getbbox())
butterfly_mask_img = butterfly_mask_img.resize((100, 100), resample=Image.Resampling.LANCZOS)
butterfly_mask_img = butterfly_mask_img.rotate(60, resample=Image.Resampling.BICUBIC, expand=True)

mask_img = Image.open("mask.png").convert("RGBA")
mask_img.paste(butterfly_mask_img, (200, 692), butterfly_mask_img)
mask_width, mask_height = mask_img.size
mask_alpha = mask_img.split()[-1]

target_img = Image.open("target_10.png").convert("RGBA")
target_width, target_height = target_img.size

# scale target image to cover the mask size
scale = 1.04
new_width = int(target_width * scale)
new_height = int(target_height * scale)
resized_target = target_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

# crop the resized target to the mask size
left = (new_width - mask_width) // 2 + 50
upper = (new_height - mask_height) // 2
right = left + mask_width
lower = upper + mask_height
cropped_target = resized_target.crop((left, new_height-mask_height, right, new_height))

# apply mask alpha as binary silhouette
r, g, b, a = cropped_target.split()
silhouette_img = Image.merge("RGBA", (r, g, b, mask_alpha))

# base_img = Image.open("background.webp").convert("RGBA")
# base_img.paste(silhouette_img, (0, 0), silhouette_img)

# save result
silhouette_img.save("result.png")
silhouette_img.show("Hu Tao Poster")
