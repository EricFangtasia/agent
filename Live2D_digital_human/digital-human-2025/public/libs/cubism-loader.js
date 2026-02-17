// public/libs/cubism-loader.js
console.log("🔗 正在尝试手动解构 Cubism Core...");
if (window.Live2DCubismCore) {
    window.LIVE2DCUBISMCORE = window.Live2DCubismCore;
    console.log("✅ 手动绑定成功");
}