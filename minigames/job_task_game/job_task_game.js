export default class JobTaskGame extends Phaser.Scene {
    constructor() {
        super('JobTaskGame');
        this.stepElements = [];
    }

    init(data) {
        this.taskData = data.taskData || {
            name: "Make an Espresso",
            description: "Create a perfect shot of espresso",
            image: "assets/espresso.webp",
            steps: [
                { name: "Grind the beans", image: "assets/grind_beans.webp", order: 1 },
                { name: "Tamp the grounds", image: "assets/tamp_grounds.webp", order: 2 },
                { name: "Pull the shot", image: "assets/pull_shot.webp", order: 3 },
            ]
        };
    }

    preload() {
        this.load.image('taskImage', this.taskData.image);
        this.taskData.steps.forEach(step => {
            this.load.image(step.name, step.image);
        });
        this.load.image('up_arrow', 'assets/arrow_up.svg');
        this.load.image('down_arrow', 'assets/arrow_down.svg');
    }

    create() {
        const { width, height } = this.scale;

        this.cameras.main.setBackgroundColor('#2C3E50');

        this.add.text(width / 2, 50, this.taskData.name, {
            fontSize: '36px',
            fontFamily: 'Arial',
            color: '#ECF0F1',
            fontWeight: 'bold'
        }).setOrigin(0.5);

        this.add.text(width / 2, 100, this.taskData.description, {
            fontSize: '20px',
            fontFamily: 'Arial',
            color: '#BDC3C7'
        }).setOrigin(0.5);

        const taskImage = this.add.image(width - 120, 100, 'taskImage').setOrigin(0.5);
        taskImage.setScale(Math.min(180 / taskImage.width, 180 / taskImage.height));

        const gridBaseY = 200;
        const spacing = 100;

        const shuffledSteps = Phaser.Utils.Array.Shuffle(this.taskData.steps.slice());

        shuffledSteps.forEach((step, index) => {
            const stepElement = this.createStepElement(step, width / 2, gridBaseY + index * spacing);
            this.stepElements.push(stepElement);
        });

        // Initially update arrows
        this.updateArrows();

        this.createCheckButton(width / 2, height - 50);
    }

    createStepElement(step, x, y) {
        const stepElement = this.add.container(x, y);

        const bg = this.add.rectangle(0, 0, 500, 80, 0x34495E, 1).setOrigin(0.5);
        bg.setStrokeStyle(2, 0x2980B9);

        const image = this.add.image(-220, 0, step.name).setOrigin(0.5);
        const scaleFactor = Math.min(70 / image.width, 70 / image.height);
        image.setScale(scaleFactor);

        const text = this.add.text(10, 0, step.name, {
            fontSize: '20px',
            fontFamily: 'Arial',
            color: '#ECF0F1'
        }).setOrigin(0, 0.5);

        // Add up and down arrow buttons
        const upArrow = this.add.image(220, -20, 'up_arrow').setInteractive({ useHandCursor: true }).setScale(0.6);
        const downArrow = this.add.image(220, 20, 'down_arrow').setInteractive({ useHandCursor: true }).setScale(0.6);

        // Set up click event for up arrow
        upArrow.on('pointerdown', () => {
            this.moveStepUp(stepElement);
        });

        // Set up click event for down arrow
        downArrow.on('pointerdown', () => {
            this.moveStepDown(stepElement);
        });

        stepElement.add([ bg, image, text, upArrow, downArrow ]);
        stepElement.setSize(500, 80);

        stepElement.upArrow = upArrow;
        stepElement.downArrow = downArrow;
        stepElement.stepData = step;

        return stepElement;
    }

    moveStepUp(stepElement) {
        const index = this.stepElements.indexOf(stepElement);
        if (index > 0) {
            // Swap positions with the item above
            const aboveElement = this.stepElements[ index - 1 ];
            this.swapElements(stepElement, aboveElement);
            this.updateArrows();
        }
    }

    moveStepDown(stepElement) {
        const index = this.stepElements.indexOf(stepElement);
        if (index < this.stepElements.length - 1) {
            // Swap positions with the item below
            const belowElement = this.stepElements[ index + 1 ];
            this.swapElements(stepElement, belowElement);
            this.updateArrows();
        }
    }

    swapElements(element1, element2) {
        // Swap the y positions
        const tempY = element1.y;
        element1.y = element2.y;
        element2.y = tempY;

        // Swap their positions in the stepElements array
        const index1 = this.stepElements.indexOf(element1);
        const index2 = this.stepElements.indexOf(element2);

        this.stepElements[ index1 ] = element2;
        this.stepElements[ index2 ] = element1;

        // Animate the swap
        this.tweens.add({
            targets: element1,
            y: element1.y,
            duration: 300,
            ease: 'Power2'
        });

        this.tweens.add({
            targets: element2,
            y: element2.y,
            duration: 300,
            ease: 'Power2'
        });
    }

    updateArrows() {
        this.stepElements.forEach((element, index) => {
            element.upArrow.setVisible(index > 0);
            element.downArrow.setVisible(index < this.stepElements.length - 1);
        });
    }

    checkOrder(draggedElement) {
        const sortedElements = this.stepElements.slice().sort((a, b) => a.y - b.y);

        const baseY = 200;
        const spacing = 100;

        sortedElements.forEach((element, index) => {
            const targetY = baseY + index * spacing;
            const targetX = this.dropArea.x;

            if (element !== draggedElement) {
                this.tweens.add({
                    targets: element,
                    x: targetX,
                    y: targetY,
                    duration: 300,
                    ease: 'Power2'
                });
            } else {
                // Snap dragged element into place when dropped
                draggedElement.x = targetX;
                draggedElement.y = targetY;
            }
        });
    }

    createCheckButton(x, y) {
        const button = this.add.container(x, y);
        const bg = this.add.rectangle(0, 0, 200, 60, 0x27AE60, 1).setOrigin(0.5);
        const text = this.add.text(0, 0, 'Check Order', {
            fontSize: '24px',
            fontFamily: 'Arial',
            color: '#ECF0F1'
        }).setOrigin(0.5);

        button.add([ bg, text ]);
        button.setSize(200, 60);
        button.setInteractive(new Phaser.Geom.Rectangle(-100, -30, 200, 60), Phaser.Geom.Rectangle.Contains);

        button.on('pointerover', () => {
            bg.setFillStyle(0x2ECC71);
        });
        button.on('pointerout', () => {
            bg.setFillStyle(0x27AE60);
        });
        button.on('pointerdown', () => {
            this.validateOrder();
        });

        return button;
    }

    validateOrder() {
        const currentOrder = this.stepElements.slice().sort((a, b) => a.y - b.y);
        const isCorrect = currentOrder.every((element, index) => element.stepData.order === index + 1);

        if (isCorrect) {
            this.showFeedback("Correct! You've completed the task successfully!", 0x27AE60);
        } else {
            this.showFeedback("Not quite right. Try again!", 0xE74C3C);
        }
    }

    showFeedback(message, color) {
        const { width, height } = this.scale;
        const overlay = this.add.rectangle(width / 2, height / 2, width, height, 0x000000, 0.7).setOrigin(0.5);
        const feedback = this.add.container(width / 2, height / 2);

        const bg = this.add.rectangle(0, 0, 400, 200, color, 1).setOrigin(0.5);
        const text = this.add.text(0, 0, message, {
            fontSize: '24px',
            fontFamily: 'Arial',
            color: '#ECF0F1',
            align: 'center',
            wordWrap: { width: 380 }
        }).setOrigin(0.5);

        feedback.add([ bg, text ]);
        feedback.setAlpha(0);
        feedback.setScale(0.5);

        this.tweens.add({
            targets: feedback,
            alpha: 1,
            scale: 1,
            duration: 300,
            ease: 'Back.out'
        });

        this.time.delayedCall(3000, () => {
            this.tweens.add({
                targets: [ overlay, feedback ],
                alpha: 0,
                duration: 300,
                onComplete: () => {
                    overlay.destroy();
                    feedback.destroy();
                }
            });
        });
    }
}