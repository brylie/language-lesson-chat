from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class StepBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=True, help_text="Name of the step",)
    image = ImageChooserBlock(required=True, help_text="Image for the step",)
    order = blocks.IntegerBlock(
        required=True, help_text="Correct order of the step", min_value=1,)


class StepOrderGameBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Title of the sequence",)
    description = blocks.TextBlock(
        required=True, help_text="Description of the sequencing task",)
    main_image = ImageChooserBlock(
        required=True, help_text="Main image for the sequencing task",)
    steps = blocks.ListBlock(StepBlock())

    class Meta:
        template = 'minigames/blocks/step_order_game.html'
        icon = 'order'
        label = 'Step Order Game'
