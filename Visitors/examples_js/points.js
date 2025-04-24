// Generated JavaScript from Carlos

class Point {
  constructor(x, y) {
    this.x = x;
    this.y = y;
  }
}

const triangle = [new Point(1, 2), new Point(3, 5), new Point(-3, 8)];

for (const p of triangle) {
  console.log(p);
}
