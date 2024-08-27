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
        this.load.image('dragHandle', 'assets/arrow_down_up.svg');
    }

    create() {
        const { width, height } = this.scale;

        // Set background color
        this.cameras.main.setBackgroundColor('#2C3E50');

        // Add task information
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

        // Create step elements
        const shuffledSteps = Phaser.Utils.Array.Shuffle(this.taskData.steps.slice());
        const baseY = 200;
        const spacing = 100;

        shuffledSteps.forEach((step, index) => {
            const stepElement = this.createStepElement(step, width / 2, baseY + index * spacing);
            this.stepElements.push(stepElement);
        });

        // Add drag events
        this.input.on('dragstart', this.onDragStart, this);
        this.input.on('drag', this.onDrag, this);
        this.input.on('dragend', this.onDragEnd, this);

        // Add "Check Order" button
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

        const dragHandle = this.add.image(230, 0, 'dragHandle').setScale(0.6);

        stepElement.add([ bg, image, text, dragHandle ]);
        stepElement.setSize(500, 80);

        // Make the entire stepElement interactive and draggable
        stepElement.setInteractive({ useHandCursor: true });
        this.input.setDraggable(stepElement);

        // Add hover effect
        stepElement.on('pointerover', () => {
            bg.setStrokeStyle(3, 0x3498DB);
            this.tweens.add({
                targets: stepElement,
                scaleX: 1.02,
                scaleY: 1.02,
                duration: 100,
                ease: 'Power2'
            });
        });

        stepElement.on('pointerout', () => {
            bg.setStrokeStyle(2, 0x2980B9);
            this.tweens.add({
                targets: stepElement,
                scaleX: 1,
                scaleY: 1,
                duration: 100,
                ease: 'Power2'
            });
        });

        stepElement.originalY = stepElement.y;
        stepElement.stepData = step;

        return stepElement;
    }

    onDragStart(pointer, gameObject) {
        gameObject.list[ 0 ].setStrokeStyle(3, 0x3498DB);
        gameObject.depth = 1;
        this.tweens.add({
            targets: gameObject,
            scaleX: 1.05,
            scaleY: 1.05,
            duration: 200,
            ease: 'Power2'
        });
    }

    onDrag(pointer, gameObject, dragX, dragY) {
        gameObject.y = dragY;
        this.checkOrder(gameObject);
    }

    onDragEnd(pointer, gameObject) {
        gameObject.list[ 0 ].setStrokeStyle(2, 0x2980B9);
        gameObject.depth = 0;
        this.tweens.add({
            targets: gameObject,
            scaleX: 1,
            scaleY: 1,
            duration: 200,
            ease: 'Power2'
        });
        this.checkOrder(gameObject);
    }

    checkOrder(draggedElement) {
        const sortedElements = this.stepElements.slice().sort((a, b) => a.y - b.y);

        sortedElements.forEach((element, index) => {
            const targetY = index * 100 + 200;
            if (element !== draggedElement) {
                this.tweens.add({
                    targets: element,
                    y: targetY,
                    duration: 300,
                    ease: 'Power2'
                });
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