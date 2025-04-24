// Generated JavaScript from Carlos

const languageName = "Carlos";

function greeting() {
  return (() => { const _arr = ["Welcome", "こんにちは", "Bienvenido"]; return _arr[Math.floor(Math.random() * _arr.length)]; })();
}

console.log("👋👋👋")

for (let _i = 0; _i < 5; _i++) {
  console.log((greeting() + " ") + languageName);
}
