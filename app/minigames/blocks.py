from django.utils.http import urlencode
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class BaseMinigameBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Title of the minigame")
    description = blocks.TextBlock(required=False, help_text="Description of the minigame")
    instructions = blocks.TextBlock(required=False, help_text="Instructions for the minigame")


class StepBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=True, help_text="Name of the step")
    image = ImageChooserBlock(required=True, help_text="Image for the step")


class StepOrderGameBlock(BaseMinigameBlock):
    main_image = ImageChooserBlock(required=True, help_text="Main image for the sequencing task")
    steps = blocks.ListBlock(StepBlock())

    class Meta:
        template = "minigames/blocks/step_order_game.html"
        icon = "order"
        label = "Step Order Game"


class QueryParamBlock(blocks.StructBlock):
    key = blocks.CharBlock(required=True, help_text="Query parameter key")
    value = blocks.CharBlock(required=True, help_text="Query parameter value")


class IframeBlock(BaseMinigameBlock):
    url = blocks.URLBlock(required=True, help_text="URL for the iframe src")
    query_params = blocks.ListBlock(
        QueryParamBlock(required=False),
        help_text="Optional query parameters",
        default=[],
        required=False,
    )

    class Meta:
        template = "minigames/blocks/iframe_block.html"
        icon = "link"
        label = "Iframe"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        url = value["url"]
        query_params = value.get("query_params", None)

        if query_params and isinstance(query_params, list):
            encoded_params = urlencode({param["key"]: param["value"] for param in query_params})
            url = f"{url}?{encoded_params}"

        context["iframe_url"] = url
        return context
