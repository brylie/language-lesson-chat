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
    }

    create() {
        const { width, height } = this.scale;

        this.cameras.main.setBackgroundColor('#2C3E50');

        // Header row
        const headerHeight = height * 0.25;
        this.createHeader(width, headerHeight);

        // Steps row
        const stepsHeight = height * 0.65;
        this.createSteps(width, headerHeight, stepsHeight);

        // Footer row
        const footerHeight = height * 0.1;
        this.createFooter(width, height - footerHeight, footerHeight);
    }

    createHeader(width, height) {
        const padding = 20;

        // Title and description
        const titleText = this.add.text(padding, padding, this.taskData.name, {
            fontSize: '32px',
            fontFamily: 'Arial',
            color: '#ECF0F1',
            fontWeight: 'bold'
        });

        const descriptionText = this.add.text(padding, titleText.y + titleText.height + 10, this.taskData.description, {
            fontSize: '18px',
            fontFamily: 'Arial',
            color: '#BDC3C7',
            wordWrap: { width: width * 0.6 }
        });

        // Task image
        const imageWidth = width * 0.3;
        const imageHeight = height - padding * 2;
        const taskImage = this.add.image(width - padding, padding, 'taskImage')
            .setOrigin(1, 0);

        // Preserve aspect ratio
        const scale = Math.min(imageWidth / taskImage.width, imageHeight / taskImage.height);
        taskImage.setScale(scale);
    }

    createSteps(width, startY, height) {
        const padding = 20;
        const stepWidth = width - padding * 2;
        const stepHeight = 70;
        const spacing = 10;

        const shuffledSteps = Phaser.Utils.Array.Shuffle(this.taskData.steps.slice());

        shuffledSteps.forEach((step, index) => {
            const y = startY + padding + index * (stepHeight + spacing);
            const stepElement = this.createStepElement(step, width / 2, y, stepWidth, stepHeight);
            this.stepElements.push(stepElement);
        });

        this.updateArrows();
    }

    createStepElement(step, x, y, width, height) {
        const stepElement = this.add.container(x, y);

        const bg = this.add.rectangle(0, 0, width, height, 0x34495E, 1).setOrigin(0.5);
        bg.setStrokeStyle(2, 0x2980B9);

        const image = this.add.image(-width / 2 + height / 2, 0, step.name).setOrigin(0.5);
        const scaleFactor = Math.min((height - 10) / image.height, (height - 10) / image.width);
        image.setScale(scaleFactor);

        const text = this.add.text(10 - width / 2 + height, 0, step.name, {
            fontSize: '18px',
            fontFamily: 'Arial',
            color: '#ECF0F1'
        }).setOrigin(0, 0.5);

        const triangleSize = 15;
        const arrowTint = 0xBDC3C7;

        // Create up triangle
        const upTriangle = this.add.graphics();
        upTriangle.fillStyle(arrowTint, 1);
        upTriangle.beginPath();
        upTriangle.moveTo(0, -triangleSize / 2); // Top vertex
        upTriangle.lineTo(-triangleSize / 2, triangleSize / 2); // Bottom left vertex
        upTriangle.lineTo(triangleSize / 2, triangleSize / 2); // Bottom right vertex
        upTriangle.closePath();
        upTriangle.fillPath();
        upTriangle.setPosition(width / 2 - 30, -height / 4);

        // Define hit area for the up triangle
        const upTriangleHitArea = new Phaser.Geom.Triangle(0, -triangleSize / 2, -triangleSize / 2, triangleSize / 2, triangleSize / 2, triangleSize / 2);
        upTriangle.setInteractive(upTriangleHitArea, Phaser.Geom.Triangle.Contains);

        // Create down triangle
        const downTriangle = this.add.graphics();
        downTriangle.fillStyle(arrowTint, 1);
        downTriangle.beginPath();
        downTriangle.moveTo(0, triangleSize / 2); // Bottom vertex
        downTriangle.lineTo(-triangleSize / 2, -triangleSize / 2); // Top left vertex
        downTriangle.lineTo(triangleSize / 2, -triangleSize / 2); // Top right vertex
        downTriangle.closePath();
        downTriangle.fillPath();
        downTriangle.setPosition(width / 2 - 30, height / 4);

        // Define hit area for the down triangle
        const downTriangleHitArea = new Phaser.Geom.Triangle(0, triangleSize / 2, -triangleSize / 2, -triangleSize / 2, triangleSize / 2, -triangleSize / 2);
        downTriangle.setInteractive(downTriangleHitArea, Phaser.Geom.Triangle.Contains);

        // Set up interaction
        upTriangle.on('pointerdown', () => this.moveStepUp(stepElement));
        downTriangle.on('pointerdown', () => this.moveStepDown(stepElement));

        stepElement.add([ bg, image, text, upTriangle, downTriangle ]);
        stepElement.setSize(width, height);

        stepElement.upTriangle = upTriangle;
        stepElement.downTriangle = downTriangle;
        stepElement.stepData = step;

        return stepElement;
    }

    createFooter(width, y, height) {
        this.createCheckButton(width / 2, y + height / 2);
    }

    moveStepUp(stepElement) {
        const index = this.stepElements.indexOf(stepElement);
        if (index > 0) {
            const aboveElement = this.stepElements[ index - 1 ];
            this.swapElements(stepElement, aboveElement);
            this.updateArrows();
        }
    }

    moveStepDown(stepElement) {
        const index = this.stepElements.indexOf(stepElement);
        if (index < this.stepElements.length - 1) {
            const belowElement = this.stepElements[ index + 1 ];
            this.swapElements(stepElement, belowElement);
            this.updateArrows();
        }
    }

    swapElements(element1, element2) {
        const tempY = element1.y;
        element1.y = element2.y;
        element2.y = tempY;

        const index1 = this.stepElements.indexOf(element1);
        const index2 = this.stepElements.indexOf(element2);

        this.stepElements[ index1 ] = element2;
        this.stepElements[ index2 ] = element1;

        this.tweens.add({
            targets: [ element1, element2 ],
            y: element => element.y,
            duration: 200,
            ease: 'Power2'
        });
    }

    updateArrows() {
        this.stepElements.forEach((element, index) => {
            element.upTriangle.setVisible(index > 0);
            element.downTriangle.setVisible(index < this.stepElements.length - 1);
        });
    }

    createCheckButton(x, y) {
        const buttonWidth = 180;
        const buttonHeight = 50;

        const button = this.add.container(x, y);
        const bg = this.add.rectangle(0, 0, buttonWidth, buttonHeight, 0x27AE60, 1).setOrigin(0.5);
        const text = this.add.text(0, 0, 'Check Order', {
            fontSize: '20px',
            fontFamily: 'Arial',
            color: '#ECF0F1'
        }).setOrigin(0.5);

        button.add([ bg, text ]);

        // Create a larger hit area for the button
        const hitArea = new Phaser.Geom.Rectangle(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight);
        button.setInteractive(hitArea, Phaser.Geom.Rectangle.Contains);

        button.on('pointerover', () => bg.setFillStyle(0x2ECC71));
        button.on('pointerout', () => bg.setFillStyle(0x27AE60));
        button.on('pointerdown', () => this.validateOrder());

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

        const bg = this.add.rectangle(0, 0, width * 0.8, height * 0.3, color, 1).setOrigin(0.5);
        const text = this.add.text(0, 0, message, {
            fontSize: '24px',
            fontFamily: 'Arial',
            color: '#ECF0F1',
            align: 'center',
            wordWrap: { width: width * 0.7 }
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