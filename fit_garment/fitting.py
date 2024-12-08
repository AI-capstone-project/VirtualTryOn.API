""" See below for the parts that are changed by us"""

from utils_stableviton import get_mask_location, get_batch, tensor2img, center_crop
from cldm.plms_hacked import PLMSSampler
from cldm.model import create_model
from preprocess.DensePose.apply_net_gradio import DensePose4Gradio
from preprocess.humanparsing.run_parsing import Parsing
from preprocess.openpose.run_openpose import OpenPose
from preprocess.image_helper import ImagePreprocessor

import sys
import time
from os.path import join as opj
from pathlib import Path

import torch
from omegaconf import OmegaConf
from PIL import Image
print(torch.cuda.is_available(), torch.cuda.device_count())


PROJECT_ROOT = Path(__file__).absolute().parents[1].absolute()
sys.path.insert(0, str(PROJECT_ROOT))

IMG_H = 1024//2
IMG_W = 768//2

# openpose_model_hd = OpenPose(0)
# openpose_model_hd.preprocessor.body_estimation.model.to('cuda')
# parsing_model_hd = Parsing(0)
# densepose_model_hd = DensePose4Gradio(
#     cfg='/code/fit_garment/preprocess/DensePose/configs/densepose_rcnn_R_50_FPN_s1x.yaml',
#     model='https://dl.fbaipublicfiles.com/densepose/densepose_rcnn_R_50_FPN_s1x/165712039/model_final_162be9.pkl',
# )

category_dict = ['upperbody']
category_dict_utils = ['upper_body']

# #### model init >>>>
config = OmegaConf.load("/code/fit_garment/config/VITON.yaml")
config.model.params.img_H = IMG_H
config.model.params.img_W = IMG_W
params = config.model.params

# model = create_model(config_path=None, config=config)
# model.load_state_dict(torch.load("/code/fit_garment/checkpoints/VITONHD_1024.ckpt", map_location="cuda:0")["state_dict"])
# model = model.cuda()
# model.eval()
# sampler2 = PLMSSampler(model)

"""
We extracted the image processing in the below code,
but rest of the code is taken from https://huggingface.co/spaces/rlawjdghek/StableVITON/blob/main/app.py
"""
def stable_viton_model_hd(
        batch,
        n_steps,
):
    z, cond = model.get_input(batch, params.first_stage_key)
    z = z
    bs = z.shape[0]
    c_crossattn = cond["c_crossattn"][0][:bs]
    if c_crossattn.ndim == 4:
        c_crossattn = model.get_learned_conditioning(c_crossattn)
        cond["c_crossattn"] = [c_crossattn]
    uc_cross = model.get_unconditional_conditioning(bs)
    uc_full = {"c_concat": cond["c_concat"], "c_crossattn": [uc_cross]}
    uc_full["first_stage_cond"] = cond["first_stage_cond"]
    for k, v in batch.items():
        if isinstance(v, torch.Tensor):
            batch[k] = v.cuda()
    sampler2.model.batch = batch

    ts = torch.full((1,), 999, device=z.device, dtype=torch.long)
    start_code = model.q_sample(z, ts)
    torch.cuda.empty_cache()
    output, _, _ = sampler2.sample(
        n_steps,
        bs,
        (4, IMG_H//8, IMG_W//8),
        cond,
        x_T=start_code,
        verbose=False,
        eta=0.0,
        unconditional_conditioning=uc_full,
    )

    output = model.decode_first_stage(output)
    output = tensor2img(output)
    pil_output = Image.fromarray(output)
    return pil_output


def process_hd(vton_img, garm_img, n_steps):
    global IncrementalID
    return vton_img
    model_type = 'hd'
    category = 0  # 0:upperbody;

    stt = time.time()
    print('load images... ', end='')

    preprocessor = ImagePreprocessor(IMG_W, IMG_H)

    vton_img = preprocessor.process_vton_image(vton_img)
    garm_img = preprocessor.process_garm_image(garm_img)

    print('%.2fs' % (time.time() - stt))

    stt = time.time()
    print('get agnostic map... ', end='')
    keypoints = openpose_model_hd(vton_img)
    model_parse, _ = parsing_model_hd(vton_img)
    mask, mask_gray = get_mask_location(
        model_type, category_dict_utils[category], model_parse, keypoints, radius=5)
    mask = mask.resize((IMG_W, IMG_H), Image.NEAREST)
    mask_gray = mask_gray.resize((IMG_W, IMG_H), Image.NEAREST)
    masked_vton_img = Image.composite(
        mask_gray, vton_img, mask)  # agnostic map
    print('%.2fs' % (time.time() - stt))

    stt = time.time()
    print('get densepose... ', end='')
    vton_img = vton_img.resize((IMG_W, IMG_H))  # size for densepose
    densepose = densepose_model_hd.execute(vton_img)  # densepose
    print('%.2fs' % (time.time() - stt))

    batch = get_batch(
        vton_img,
        garm_img,
        densepose,
        masked_vton_img,
        mask,
        IMG_H,
        IMG_W
    )

    sample = stable_viton_model_hd(
        batch,
        n_steps,
    )

    # Convert to white everything from sample that is outside of densepose
    densepose_mask = densepose.convert("L").point(
        lambda x: 255 if x > 0 else 0, mode='1')
    sample = Image.composite(sample, Image.new(
        "RGB", sample.size, "white"), densepose_mask)

    # sample.save(f"../ID-{1}.png", 'PNG')

    return sample


if __name__ == "__main__":
    import os
    import shutil

    # Define paths
    garment_image_path = '.examples/garment/garment1.jpg'
    model_image_path = '.examples/model/model1.jpg'
    output_folder = './output'

    # Ensure the output folder is empty
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    # Perform the fitting
    result_image = process_hd(model_image_path, garment_image_path, 20)

    # Save the result
    result_image_path = os.path.join(output_folder, 'result.jpg')
    result_image.save(result_image_path)

    print(f"Result image saved to {result_image_path}")
