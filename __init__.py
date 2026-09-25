from PIL import Image
import numpy as np
import torch


class CleanAlpha:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (
                    "IMAGE",
                    {
                        "tooltip": "RGB or RGBA image to process."
                    },
                ),

                "maximum": (
                    "INT",
                    {
                        "default": 240,
                        "min": 0,
                        "max": 255,
                        "step": 1,
                        "tooltip": (
                            "Alpha values greater than this value "
                            "are changed to 255. "
                            "Set to 255 to disable this operation."
                        ),
                    },
                ),

                "minimum": (
                    "INT",
                    {
                        "default": 15,
                        "min": 0,
                        "max": 255,
                        "step": 1,
                        "tooltip": (
                            "Alpha values lower than this value "
                            "are changed to 0. "
                            "Set to 0 to disable this operation."
                        ),
                    },
                ),

                "convert_to_rgb": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": (
                            "Convert the image to RGB when every alpha "
                            "value is 255 after cleaning."
                        ),
                    },
                ),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "clean_alpha"
    CATEGORY = "Image/Alpha"

    def clean_alpha(
        self,
        image,
        maximum,
        minimum,
        convert_to_rgb,
    ):
        # ---------------------------------------------------------
        # ComfyUI provides the image as a tensor with shape:
        #
        # [batch, height, width, channels]
        #
        # This node is intended for single-image use, so take
        # the first image.
        # ---------------------------------------------------------

        img = image[0]

        # Convert ComfyUI's 0.0-1.0 tensor to PIL-compatible
        # uint8 values in the 0-255 range.
        img_array = (
            img.detach()
            .cpu()
            .numpy()
            .clip(0.0, 1.0)
            * 255.0
        ).round().astype(np.uint8)

        channels = img_array.shape[-1]

        # ---------------------------------------------------------
        # RGB input
        #
        # There is no alpha channel, so return it unchanged.
        # ---------------------------------------------------------

        if channels == 3:
            return (image,)

        # ---------------------------------------------------------
        # RGBA input
        # ---------------------------------------------------------

        if channels != 4:
            raise ValueError(
                "Clean Alpha expects an RGB or RGBA image, "
                f"but received an image with {channels} channels."
            )

        pil_image = Image.fromarray(
            img_array,
            "RGBA",
        )

        # Separate RGB and alpha.
        rgb = pil_image.convert("RGB")
        alpha = pil_image.getchannel("A")

        # ---------------------------------------------------------
        # Maximum
        #
        # Alpha > maximum becomes 255.
        #
        # maximum == 255 disables this operation.
        # ---------------------------------------------------------

        if maximum != 255:
            alpha = alpha.point(
                lambda value: (
                    255
                    if value > maximum
                    else value
                )
            )

        # ---------------------------------------------------------
        # Minimum
        #
        # Alpha < minimum becomes 0.
        #
        # minimum == 0 disables this operation.
        # ---------------------------------------------------------

        if minimum != 0:
            alpha = alpha.point(
                lambda value: (
                    0
                    if value < minimum
                    else value
                )
            )

        # ---------------------------------------------------------
        # Determine whether every alpha value is 255.
        # ---------------------------------------------------------

        alpha_array = np.asarray(alpha)

        all_opaque = bool(
            np.all(alpha_array == 255)
        )

        # ---------------------------------------------------------
        # Convert to RGB when possible.
        # ---------------------------------------------------------

        if convert_to_rgb and all_opaque:
            result = rgb

        else:
            result = Image.merge(
                "RGBA",
                (
                    rgb.getchannel("R"),
                    rgb.getchannel("G"),
                    rgb.getchannel("B"),
                    alpha,
                ),
            )

        # ---------------------------------------------------------
        # Convert PIL image back to ComfyUI IMAGE format.
        # ---------------------------------------------------------

        result_array = np.asarray(
            result,
            dtype=np.uint8,
        )

        result_tensor = (
            torch.from_numpy(result_array)
            .float()
            / 255.0
        )

        # Restore the batch dimension expected by ComfyUI.
        result_tensor = result_tensor.unsqueeze(0)

        return (result_tensor,)


NODE_CLASS_MAPPINGS = {
    "CleanAlpha": CleanAlpha,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CleanAlpha": "Clean Alpha",
}
