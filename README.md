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
