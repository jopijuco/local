
// const object = { a: 1, b: 2, c: 3 };

// for (const property in object) {
//   console.log(`${property}: ${object[property]}`);
// }


var addButton = document.getElementById("add_button");
addButton.addEventListener('click', () => {    
    var n = parseInt(document.getElementById("myBasket").innerHTML);
    n = n+1
    document.getElementById("myBasket").innerHTML = n;
});

var emptyButton = document.getElementById("empty_button");
emptyButton.addEventListener('click', () => {    
    console.log("empty basket")
});

