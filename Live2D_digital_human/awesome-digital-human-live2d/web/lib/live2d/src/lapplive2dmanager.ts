/**
 * Copyright(c) Live2D Inc. All rights reserved.
 *
 * Use of this source code is governed by the Live2D Open Software license
 * that can be found at https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html.
 */

import { CubismMatrix44 } from '@framework/math/cubismmatrix44';
import { ACubismMotion } from '@framework/motion/acubismmotion';
import { csmVector } from '@framework/type/csmvector';

import * as LAppDefine from './lappdefine';
import { LAppModel } from './lappmodel';
import { LAppPal } from './lapppal';
import { LAppSubdelegate } from './lappsubdelegate';
import { ResourceModel } from '@/lib/protocol';
import * as path from 'path';

/**
 * サンプルアプリケーションにおいてCubismModelを管理するクラス
 * モデル生成と破棄、タップイベントの処理、モデル切り替えを行う。
 */
export class LAppLive2DManager {
  /**
   * 現在のシーンで保持しているすべてのモデルを解放する
   */
  private releaseAllModel(): void {
    this._models.clear();
  }

  /**
   * 画面をドラッグした時の処理
   *
   * @param x 画面のX座標
   * @param y 画面のY座標
   */
  public onDrag(x: number, y: number): void {
    const model: LAppModel = this._models.at(0);
    if (model) {
      model.setDragging(x, y);
    }
  }

  /**
   * 画面をタップした時の処理
   *
   * @param x 画面のX座標
   * @param y 画面のY座標
   */
  public onTap(x: number, y: number): void {
    if (LAppDefine.DebugLogEnable) {
      LAppPal.printMessage(
        `[APP]tap point: {x: ${x.toFixed(2)} y: ${y.toFixed(2)}}`
      );
    }

    const model: LAppModel = this._models.at(0);
    if (!model) return;
    
    // 点击任意位置都触发交互
    this.playTouchReaction(model);
  }

  /**
   * 播放触摸反馈
   * @param model 被点击的模型
   */
  private playTouchReaction(model: LAppModel): void {
    console.log('[Live2D] Touch detected, playing reaction');
    
    // 随机反应话术
    const reactions = [
      "讨厌~",
      "不要这样子嘛",
      "好舒服啊",
      "哥哥我错了",
      "哈哈哈",
      "干嘛啦",
      "你在干什么",
      "不要碰我",
      "好痒啊",
      "嘿嘿~",
      "人家会害羞的啦",
      "讨厌，别摸了",
      "嗯~好舒服",
      "主人真坏",
      "再这样我要生气了哦",
      "呀~轻一点",
      "好痒好痒",
      "你想干嘛呀",
      "人家不给你摸",
      "哼~坏蛋",
      "诶嘿嘿~",
      "主人好色",
      "别闹了啦",
      "讨厌死了",
      "你好坏哦"
    ];
    
    const randomReaction = reactions[Math.floor(Math.random() * reactions.length)];
    console.log(`[Live2D] Reaction: ${randomReaction}`);
    
    // 播放表情（如果模型有的话）
    model.setRandomExpression();
    
    // 播放身体触碰动作（如果模型有的话）
    model.startRandomMotion(
      LAppDefine.MotionGroupTapBody,
      LAppDefine.PriorityForce,  // 使用高优先级确保动作播放
      null,
      null
    );
    
    // 随机选择动作（不再用锁限制，让动作更自由）
    const extraActions = [
      () => this.playShakeAnimation(model),      // 摇晃 - 最柔和
      () => this.playNodAnimation(model),        // 点头 - 可爱
      () => this.playHeadTiltAnimation(model),   // 歪头 - 卖萌
      () => this.playLeanForwardAnimation(model),// 前倾 - 互动
      () => this.playBounceAnimation(model),     // 轻弹 - 活泼
    ];
    const randomAction = extraActions[Math.floor(Math.random() * extraActions.length)];
    randomAction();
    
    // 触发自定义事件，让外部处理TTS
    const event = new CustomEvent('live2d:touch', {
      detail: { text: randomReaction }
    });
    document.dispatchEvent(event);
  }

  /**
   * 播放轻弹动画（更柔和的弹跳）
   * @param model 要弹跳的模型
   */
  private playBounceAnimation(model: LAppModel): void {
    const modelMatrix = (model as any)._modelMatrix;
    if (!modelMatrix) return;

    console.log('[Live2D] Playing bounce animation');

    const bounceHeight = 0.04;  // 轻微弹跳
    const bounceDuration = 400;
    const startTime = Date.now();

    const animateBounce = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / bounceDuration, 1.0);

      if (progress < 1.0) {
        // 弹性缓动 - 更自然的弹跳
        const easeOutBounce = (t: number): number => {
          const n1 = 7.5625;
          const d1 = 2.75;
          if (t < 1 / d1) {
            return n1 * t * t;
          } else if (t < 2 / d1) {
            return n1 * (t -= 1.5 / d1) * t + 0.75;
          } else if (t < 2.5 / d1) {
            return n1 * (t -= 2.25 / d1) * t + 0.9375;
          } else {
            return n1 * (t -= 2.625 / d1) * t + 0.984375;
          }
        };
        const bounce = easeOutBounce(progress) * bounceHeight;
        modelMatrix.translateY(-bounce);  // 向上弹
        requestAnimationFrame(animateBounce);
      } else {
        modelMatrix.translateY(0);
      }
    };

    animateBounce();
  }

  /**
   * 播放跳跃动画（Y轴位移）- 改进版
   * @param model 要跳跃的模型
   */
  private playJumpAnimation(model: LAppModel): void {
    const modelMatrix = (model as any)._modelMatrix;
    if (!modelMatrix) return;

    console.log('[Live2D] Playing jump animation');

    const jumpHeight = 0.06;  // 降低跳跃高度
    const jumpDuration = 350;
    const startTime = Date.now();

    const animateJump = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / jumpDuration, 1.0);

      if (progress < 1.0) {
        // 使用 easeOutQuad 缓动使跳跃更平滑
        const easeOut = 1 - (1 - progress) * (1 - progress);
        const jump = Math.sin(easeOut * Math.PI) * jumpHeight;
        modelMatrix.translateY(-jump);
        requestAnimationFrame(animateJump);
      } else {
        modelMatrix.translateY(0);
      }
    };

    animateJump();
  }

  /**
   * 播放摇晃动画（X轴左右摇晃）- 改进版
   * @param model 要摇晃的模型
   */
  private playShakeAnimation(model: LAppModel): void {
    const modelMatrix = (model as any)._modelMatrix;
    if (!modelMatrix) return;

    console.log('[Live2D] Playing shake animation');

    const shakeAmplitude = 0.04;
    const shakeDuration = 300;
    const startTime = Date.now();

    const animateShake = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / shakeDuration, 1.0);

      if (progress < 1.0) {
        // 平滑衰减
        const decay = 1 - progress * progress;
        const shake = Math.sin(progress * Math.PI * 4) * shakeAmplitude * decay;
        modelMatrix.translateX(shake);
        requestAnimationFrame(animateShake);
      } else {
        modelMatrix.translateX(0);
      }
    };

    animateShake();
  }

  /**
   * 播放点头动画 - 改进版
   * @param model 要点头的模型
   */
  private playNodAnimation(model: LAppModel): void {
    const modelMatrix = (model as any)._modelMatrix;
    if (!modelMatrix) return;

    console.log('[Live2D] Playing nod animation');

    const nodDepth = 0.03;
    const nodDuration = 500;
    const startTime = Date.now();

    const animateNod = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / nodDuration, 1.0);

      if (progress < 1.0) {
        // 两次点头，带缓动
        const easeInOut = progress < 0.5 
          ? 2 * progress * progress 
          : 1 - Math.pow(-2 * progress + 2, 2) / 2;
        const nod = Math.sin(progress * Math.PI * 3) * nodDepth;
        modelMatrix.translateY(nod);
        requestAnimationFrame(animateNod);
      } else {
        modelMatrix.translateY(0);
      }
    };

    animateNod();
  }

  /**
   * 播放歪头动画（歪头杀）- 改进版
   * @param model 要歪头的模型
   */
  private playHeadTiltAnimation(model: LAppModel): void {
    const modelMatrix = (model as any)._modelMatrix;
    if (!modelMatrix) return;

    console.log('[Live2D] Playing head tilt animation');

    const tiltAmplitude = 0.03;
    const tiltDuration = 600;
    const startTime = Date.now();
    const direction = Math.random() > 0.5 ? 1 : -1;

    const animateTilt = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / tiltDuration, 1.0);

      if (progress < 1.0) {
        // 平滑的正弦曲线
        const tilt = Math.sin(progress * Math.PI) * tiltAmplitude * direction;
        modelMatrix.translateX(tilt);
        requestAnimationFrame(animateTilt);
      } else {
        modelMatrix.translateX(0);
      }
    };

    animateTilt();
  }

  /**
   * 播放身体前倾动画 - 改进版
   * @param model 要前倾的模型
   */
  private playLeanForwardAnimation(model: LAppModel): void {
    const modelMatrix = (model as any)._modelMatrix;
    if (!modelMatrix) return;

    console.log('[Live2D] Playing lean forward animation');

    const leanAmount = 0.03;
    const leanDuration = 500;
    const startTime = Date.now();

    const animateLean = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / leanDuration, 1.0);

      if (progress < 1.0) {
        // 平滑的前倾和恢复
        const lean = Math.sin(progress * Math.PI) * leanAmount;
        modelMatrix.translateY(lean);
        requestAnimationFrame(animateLean);
      } else {
        modelMatrix.translateY(0);
      }
    };

    animateLean();
  }

  /**
   * 播放深呼吸动画（缩放呼吸）
   * @param model 要呼吸的模型
   */
  public playBreathAnimation(model: LAppModel): void {
    const modelMatrix = (model as any)._modelMatrix;
    if (!modelMatrix) return;

    console.log('[Live2D] Playing breath animation');

    const breathAmplitude = 0.015;
    const breathDuration = 2000;   // 呼吸周期
    const startTime = Date.now();

    const animateBreath = () => {
      const elapsed = Date.now() - startTime;
      const progress = (elapsed % breathDuration) / breathDuration;

      // 正弦波呼吸
      const breath = Math.sin(progress * Math.PI * 2) * breathAmplitude;
      modelMatrix.translateY(breath);

      // 持续2个呼吸周期后停止
      if (elapsed < breathDuration * 2) {
        requestAnimationFrame(animateBreath);
      } else {
        modelMatrix.translateY(0);
      }
    };

    animateBreath();
  }

  /**
   * 播放随机动作（用于定时触发）
   */
  public playRandomAction(): void {
    if (!this._subdelegate || this._models.getSize() === 0) return;
    
    const model = this._models.at(0);
    if (!model) return;

    const actions = [
      () => this.playShakeAnimation(model),
      () => this.playNodAnimation(model),
      () => this.playHeadTiltAnimation(model),
      () => this.playLeanForwardAnimation(model),
      () => this.playBounceAnimation(model),
    ];

    const randomAction = actions[Math.floor(Math.random() * actions.length)];
    randomAction();
    
    // 同时切换表情
    model.setRandomExpression();
  }

  /**
   * 画面を更新するときの処理
   * モデルの更新処理及び描画処理を行う
   */
  public onUpdate(): void {
    const { width, height } = this._subdelegate.getCanvas();

    const projection: CubismMatrix44 = new CubismMatrix44();
    const model: LAppModel = this._models.at(0);
    if (!model) return;
    if (model.getModel()) {
      if (model.getModel().getCanvasWidth() > 1.0 && width < height) {
        // 横に長いモデルを縦長ウィンドウに表示する際モデルの横サイズでscaleを算出する
        model.getModelMatrix().setWidth(2.0);
        projection.scale(1.0, width / height);
      } else {
        projection.scale(height / width, 1.0);
      }

      // 必要があればここで乗算
      if (this._viewMatrix != null) {
        projection.multiplyByMatrix(this._viewMatrix);
      }
    }

    model.update();
    model.draw(projection); // 参照渡しなのでprojectionは変質する。
  }

  /**
   * 次のシーンに切りかえる
   * サンプルアプリケーションではモデルセットの切り替えを行う。
   */
  // public nextScene(): void {
  //   const no: number = (this._sceneIndex + 1) % LAppDefine.ModelDirSize;
  //   this.changeScene(no);
  // }

  /**
   * シーンを切り替える
   * サンプルアプリケーションではモデルセットの切り替えを行う。
   * @param index
   */
  // private changeScene(index: number): void {
  //   this._sceneIndex = index;

  //   if (LAppDefine.DebugLogEnable) {
  //     LAppPal.printMessage(`[APP]model index: ${this._sceneIndex}`);
  //   }

  //   // ModelDir[]に保持したディレクトリ名から
  //   // model3.jsonのパスを決定する。
  //   // ディレクトリ名とmodel3.jsonの名前を一致させておくこと。
  //   const model: string = LAppDefine.ModelDir[index];
  //   const modelPath: string = LAppDefine.ResourcesPath + model + '/';
  //   let modelJsonName: string = LAppDefine.ModelDir[index];
  //   modelJsonName += '.model3.json';

  //   this.releaseAllModel();
  //   const instance = new LAppModel();
  //   instance.setSubdelegate(this._subdelegate);
  //   instance.loadAssets(modelPath, modelJsonName);
  //   this._models.pushBack(instance);
  // }

  public setViewMatrix(m: CubismMatrix44) {
    for (let i = 0; i < 16; i++) {
      this._viewMatrix.getArray()[i] = m.getArray()[i];
    }
  }

  /**
   * モデルの追加
   */
  // public addModel(sceneIndex: number = 0): void {
  //   this._sceneIndex = sceneIndex;
  //   this.changeScene(this._sceneIndex);
  // }

  /**
   * コンストラクタ
   */
  public constructor() {
    this._subdelegate = null;
    this._viewMatrix = new CubismMatrix44();
    this._models = new csmVector<LAppModel>();
    this._character = null;
    // this._sceneIndex = 0;
  }

  /**
   * 解放する。
   */
  public release(): void {}

  /**
   * 初期化する。
   * @param subdelegate
   */
  public initialize(subdelegate: LAppSubdelegate): void {
    this._subdelegate = subdelegate;
    this.changeCharacter(this._character);
  }

  public changeCharacter(character: ResourceModel | null) {
    if (character == null) {
      this.releaseAllModel();
      return;
    }
    let dir = path.dirname(character.link) + "/";
    let modelJsonName: string = `${character.name}.model3.json`;
    if (LAppDefine.DebugLogEnable) {
      LAppPal.printMessage(`[APP]model json: ${modelJsonName}`);
    }

    this.releaseAllModel();
    const instance = new LAppModel();
    instance.setSubdelegate(this._subdelegate);
    instance.loadAssets(dir, modelJsonName);
    this._models.pushBack(instance);
    this._character = character;
  }

  /**
   * 获取当前模型
   */
  public getCurrentModel(): LAppModel | null {
    if (this._models.getSize() > 0) {
      return this._models.at(0);
    }
    return null;
  }

  /**
   * 自身が所属するSubdelegate
   */
  private _subdelegate: LAppSubdelegate;

  _viewMatrix: CubismMatrix44; // モデル描画に用いるview行列
  _models: csmVector<LAppModel>; // モデルインスタンスのコンテナ
  // private _sceneIndex: number; // 表示するシーンのインデックス値
  private _character: ResourceModel | null;

  // モーション再生開始のコールバック関数
  beganMotion = (self: ACubismMotion): void => {
    LAppPal.printMessage('Motion Began');
  };
  // モーション再生終了のコールバック関数
  finishedMotion = (self: ACubismMotion): void => {
    LAppPal.printMessage('Motion Finished');
  };
}
