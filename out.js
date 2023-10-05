console.log('you are emitting something...')
console.log('How many fibonacci numbers do you want?');
console.log('');
let nums = 50;
let a = 0;
let b = 1;
while (nums>0) {
console.log(a);
let c = a+b;
a = b;
b = c;
nums = nums-1;
}
