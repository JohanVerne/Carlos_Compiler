// Generated JavaScript from Carlos

const languageName = "Carlos";

class Vector {
  constructor(x, y, label) {
    this.x = x;
    this.y = y;
    this.label = label;
  }
}

function newVector(x, y, label) {
  return new Vector(x, y, label);
}

function magnitude(v) {
  return Math.sqrt((v.x * v.x) + (v.y * v.y));
}

function scaleVector(v, factor) {
  let newX = v.x * factor;
  let newY = v.y * factor;
  return new Vector(newX, newY, v.label);
}

function testOptional(flag) {
  if (flag) {
    return 42;
  } else {
    return null;
  }
}

function processArray(a) {
  let sum = 0;
  for (let i = 0; i < a.length; i++) {
    sum = sum + a[i];
  }
  return sum;
}

function stringFun(s) {
  let result = "";
  let cp = [...s].map(c => c.codePointAt(0));
  for (const cpVal of cp) {
    result = result + (cpVal % 2) === 0 ? "E" : "O";
  }
  return result;
}

function complexCondition(a, b) {
  if ((a < b) && (a !== 0)) {
    return true;
  } else if (a === b) {
    return false;
  } else {
    return !false;
  }
}

function loopDemo(n) {
  let counter = n;
  while (counter > 0) {
    console.log("Counter: " + counter);
    counter--;
  }
  for (let _i = 0; _i < 3; _i++) {
    console.log("Repeat loop iteration");
  }
}

function rangeDemo(start, end) {
  for (let i = start; i < end; i++) {
    if ((i % 2) === 0) {
      console.log("Even: " + i);
    } else {
      console.log("Odd: " + i);
    }
  }
}

function branchDemo(x) {
  if (x > 100) {
    return x - 100;
  }
  return x + 100;
}

function breakDemo(arr) {
  let total = 0;
  for (const x of arr) {
    if (x > 50) {
      break;
    }
    total = total + x;
  }
  return total;
}

function bitwiseDemo(x, y) {
  return (((x << 1) + (y >> 1)) & (x ^ y)) | (x & y);
}

{
  console.log("Testing language: " + languageName);
  let vec = newVector(3, 4, "A");
  console.log("Vector magnitude: " + magnitude(vec));
  let scaled = scaleVector(vec, 2.5);
  console.log("Scaled vector magnitude: " + magnitude(scaled));
  let opt = testOptional(true);
  console.log("Optional value: " + opt ?? -1);
  let arrSum = processArray([10, 20, 30, 40]);
  console.log("Sum of array: " + arrSum);
  console.log(stringFun("Hello, 世界"));
loopDemo(5);
rangeDemo(1, 10);
  console.log("Branch demo: " + branchDemo(50));
  console.log("Break demo: " + breakDemo([5, 10, 55, 20]));
  console.log("Bitwise demo: " + bitwiseDemo(12, 5));
}
