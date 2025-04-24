// Generated JavaScript from Carlos

let x = null;

let y = x ?? 2;

class S {
  constructor(x) {
    this.x = x;
  }
}

let z = new S(1);

let w = z?.x;

console.log(w)
