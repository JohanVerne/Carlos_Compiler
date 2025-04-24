// Generated JavaScript from Carlos

function gcd(x, y) {
  return y === 0 ? x : gcd(y, x % y);
}

console.log(gcd(5023427, 920311))
