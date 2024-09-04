const HEADER_HEIGHT_RATIO = 0.25;
const STEPS_HEIGHT_RATIO = 0.65;
const FOOTER_HEIGHT_RATIO = 0.1;

export default class StepOrderGame extends Phaser.Scene {
  constructor(config) {
    super({ key: 'StepOrderGame' });
    this.config = config;
    this.stepElements = [];
  }

  preload() {
    console.log('Preload method called');
    console.log('Config:', this.config);

    if (!this.config || !this.config.main_image || !Array.isArray(this.config.steps)) {
      console.error('Invalid game configuration');
      return;
    }

    // Load main image
    this.load.image({
      key: 'mainImage',
      url: this.config.main_image.url,
      extension: undefined
    });

    // Load step images
    this.config.steps.forEach((step, index) => {
      if (step && typeof step === 'object' && step.image && step.image.url) {
        console.log(`Loading image for step ${index}: `, step.image.url);
        this.load.image({
          key: step.image.url,
          url: step.image.url,
          extension: undefined
        });
      } else {
        console.warn(`Invalid step or missing image at index ${index}: `, step);
      }
    });
  }

  create() {
    this.cameras.main.setBackgroundColor('#2C3E50');
    this.createLayout();

    // Listen for game resize events
    this.scale.on('resize', this.resize, this);
  }

  createLayout() {
    const { width, height } = this.scale;

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

  resize(gameSize) {
    // Destroy existing layout
    this.children.removeAll(true);
    this.stepElements = [];

    // Recreate layout with new dimensions
    this.createLayout();
  }

  createHeader(width, height) {
    const padding = Math.min(20, width * 0.05);

    const titleText = this.add.text(padding, padding, this.config.title, {
      fontSize: `${Math.max(16, width * 0.04)}px`,
      fontFamily: 'Arial',
      color: '#ECF0F1',
      fontWeight: 'bold'
    });

    const descriptionText = this.add.text(padding, titleText.y + titleText.height + 10, this.config.description, {
      fontSize: `${Math.max(12, width * 0.02)}px`,
      fontFamily: 'Arial',
      color: '#BDC3C7',
      wordWrap: { width: width * 0.6 }
    });

    const imageWidth = width * 0.3;
    const imageHeight = height - padding * 2;
    const mainImage = this.add.image(width - padding, padding, 'mainImage').setOrigin(1, 0);

    const scale = Math.min(imageWidth / mainImage.width, imageHeight / mainImage.height);
    mainImage.setScale(scale);
  }

  createSteps(width, startY, height) {
    const padding = Math.min(20, width * 0.05);
    const stepWidth = width - padding * 2;
    const stepHeight = Math.min(70, height * 0.2);
    const spacing = Math.min(10, height * 0.02);

    const shuffledSteps = Phaser.Utils.Array.Shuffle(this.config.steps.slice());

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

    const image = this.add.image(-width / 2 + height / 2, 0, step.image.url).setOrigin(0.5);
    const scaleFactor = Math.min((height - 10) / image.height, (height - 10) / image.width);
    image.setScale(scaleFactor);

    const text = this.add.text(10 - width / 2 + height, 0, step.name, {
      fontSize: '18px',
      fontFamily: 'Arial',
      color: '#ECF0F1'
    }).setOrigin(0, 0.5);

    const arrowOffsetX = width / 2 - 30;
    const arrowOffsetY = height / 4;
    const triangleSize = 15;
    const hitAreaPadding = 10;

    const upTriangle = this.createArrowTriangle(arrowOffsetX, -arrowOffsetY, triangleSize, hitAreaPadding, true);
    const downTriangle = this.createArrowTriangle(arrowOffsetX, arrowOffsetY, triangleSize, hitAreaPadding, false);

    upTriangle.on('pointerdown', () => this.moveStepUp(stepElement));
    downTriangle.on('pointerdown', () => this.moveStepDown(stepElement));

    stepElement.add([ bg, image, text, upTriangle, downTriangle ]);
    stepElement.setSize(width, height);

    stepElement.upTriangle = upTriangle;
    stepElement.downTriangle = downTriangle;
    stepElement.stepData = step;

    return stepElement;
  }

  createArrowTriangle(x, y, size, padding, isUp) {
    const triangle = this.add.graphics();
    triangle.fillStyle(0xBDC3C7, 1);

    triangle.beginPath();
    if (isUp) {
      triangle.moveTo(0, -size / 2);
      triangle.lineTo(-size / 2, size / 2);
      triangle.lineTo(size / 2, size / 2);
    } else {
      triangle.moveTo(0, size / 2);
      triangle.lineTo(-size / 2, -size / 2);
      triangle.lineTo(size / 2, -size / 2);
    }
    triangle.closePath();
    triangle.fillPath();

    triangle.setPosition(x, y);

    const hitAreaSize = size + padding;
    const hitArea = new Phaser.Geom.Rectangle(-hitAreaSize / 2, -hitAreaSize / 2, hitAreaSize, hitAreaSize);
    triangle.setInteractive(hitArea, Phaser.Geom.Rectangle.Contains);

    triangle.on('pointerover', () => {
      this.input.manager.canvas.style.cursor = 'pointer';
    });

    triangle.on('pointerout', () => {
      this.input.manager.canvas.style.cursor = 'default';
    });

    return triangle;
  }

  createFooter(width, y, height) {
    this.createCheckButton(width / 2, y + height / 2, width, height);
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

  createCheckButton(x, y, width, height) {
    const buttonWidth = Math.min(180, width * 0.4);
    const buttonHeight = Math.min(50, height * 0.6);

    const button = this.add.container(x, y);
    const bg = this.add.rectangle(0, 0, buttonWidth, buttonHeight, 0x27AE60, 1).setOrigin(0.5);
    const text = this.add.text(0, 0, 'Check Order', {
      fontSize: `${Math.max(14, width * 0.03)}px`,
      fontFamily: 'Arial',
      color: '#ECF0F1'
    }).setOrigin(0.5);

    button.add([ bg, text ]);

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
      this.showFeedback("Correct! You've completed the sequence successfully!", 0x27AE60);
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
