# VirtualTryOn.API

## create_pose
    -- sample-data
        -- SMPL/models/smpl
            -- SMPL_MALE.pkl: The male SMPL model
        -- smpl_uv_20200910
            -- smpl_uv.obj: The accomnapinying SMPL model
    -- scripts
        -- dummy_data
            -- images
                MEN-Jackets_Vests...: This is the sample image SMPLITEX uses in their repository
        -- utils
            -- renderer
                -- pytorch3d_renderer.py: This is used to create a gif from an SMPL model
            -- smpl_helpers.py: This is a file that is used to create SMPL models
        -- SGHM-ResNet50.pth: https://huggingface.co/endorno/SGHM/resolve/main/SGHM-ResNet50.pth
        -- .dockerignore: A file that is used to ignore files to go into the docker image, it ignores files like the .env file which includes secrets
        -- 3d-render.sh: This is the file that is run when the texture is ready, it coordinates the python files required to create a gif from texture
        -- app.py: A fastapi app that serves APIs to the orchestration layer
        -- compute_partial_texturemap.py: Computes partial texture of an image. 
        -- create-texture.sh: This is the file that is run when we need to prepare the texture. It cooridnates multiple python files required to create texture
        -- image_to_densepose.py: Creates a densepose of an image
        -- inpaint_with_A1111.py: Uses diffusion to complete the partial texture 
        -- render_results.py: The main file for creating poses and usings utils files to generate a 3D gif
        -- stablediffusion_wrapper: A wrapper that wraps around the stable-diffusion-webui pipeline and makes calls to it in order to complete A1111's work of completing the texture. Includes the img2img and text2img abilities

## fit_garment
    -- checkpoints: The checkpoints for densepose, humanparsing, and the pretrained models go here
        -- humanparsing
            -- parsing_atr.onnx: https://huggingface.co/spaces/rlawjdghek/StableVITON/resolve/main/checkpoints/humanparsing/parsing_atr.onnx
            -- parsing_lib.onnx: https://huggingface.co/spaces/rlawjdghek/StableVITON/resolve/main/checkpoints/humanparsing/parsing_lip.onnx
        -- openpose:
            -- body_pose_model.pth: https://huggingface.co/spaces/rlawjdghek/StableVITON/resolve/main/checkpoints/openpose/ckpts/body_pose_model.pth
        -- VITONHD_1024.ckpt: https://huggingface.co/spaces/rlawjdghek/StableVITON/resolve/main/checkpoints/VITONHD_1024.ckpt
    -- cldm: Not sure
    -- config
        -- VITON.yaml: a yaml file that includes the configuration of stable-viton
    -- fit_garment_integration_tests: includes some example images for integration testing
    -- ldm: not sure
    -- preprocess:
        -- DensePose
        -- humanparsing
        -- openpose
    -- Dockerfile: This dockerfile is to only create the fit_garment image
    -- requirements-base.txt: This includes all requirements that are unlikely to change like torch or big
    -- requirements-secondary.txt: This includes all requirements that are likely to change or small. This is used in a later stage of the dockerfile to increase the speed of builds
    -- fitting.py: This is the file that coordinates every file to fit the garment to the person
    -- utils_stableviton.py: not sure

## orchestration
    -- authentication
        -- jwt_helpers.py: a class that includes reusable logic to only allow authenticated users to access them
    -- .dockerignore: a file to let docker know what files to ignore when creating the image, for example the .env file
    -- main.py: A fastapi that includes the orchestration layer and has the endpoints FE will be calling, within it, it may call fit_garment or create_pose services
    -- requirements.txt: requirements for orchestration layer
    -- Dockerfile: a dockerfile that creates the orchestration layer

## webui
    -- a copy of https://github.com/AbdBarho/stable-diffusion-webui-docker only keeping the A1111 service

# ...
    -- .editorconfig: A file that represents the standard for files. for example, every file should end with an empty line. Requires the editorconfig extension in vs code
    -- compose.yaml: A docker compose file that includes all services. It includes the download of checkpoints for webui, and the other services


# Setup
You should have docker compose. Installation guide is here: https://docs.docker.com/compose/install/linux/#install-using-the-repository
after cloning the repo `cd` into the VirtualTryOn.API directoory
1. run `docker compose --profile download up` to download necessary files for the webui pipeline
2. Download the necessary checkpoints for stableviton and put them in the correct folder of `/fit_garment`. See the links for download in the folder structure above /fit_garment/checkpoints
3. Download the necessary checkpoints for smplitex and put them in the correct folder of `/create_pose`, the the link for the download of SGHM-ResNet50.pth in the folder structure above /create_pose/
4. run `docker compose --profile orchestration --profile fit_garment --profile auto --profile create_pose watch` This will take a while
5. create an `.env` file with the secrets of supabase and duplicate it in `/create_pose/scripts` and `/orcehstration` folders within the docker containers. Because in the previous command you are doing a `watch`, when something is changed in the folder structure, it also changes your container's folder structure, so if you create the .env file in the two above folders and save them, they will be added to the containers. The other way is to use `docker cp` to copy files from host to the containers
6. attach a shell to the `fit_garment` container and run `fastapi run orchestration/main.py --reload --port 80`
7. attach a shell to the `create_pose` container and run `conda run -n smplitex --no-capture-output fastapi run app.py --reload`
8. You should now be able to open this on your host machine's browser by going to http://0.0.0.0:8000/docs
