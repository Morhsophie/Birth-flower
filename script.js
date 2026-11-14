const nameInput = document.querySelector("#nameInput");
const greeting = document.querySelector("#greeting");
const flowerScene = document.querySelector("#flowerScene");
const replayButton = document.querySelector("#replayButton");

function updateGreeting() {
  const name = nameInput.value.trim();
  greeting.textContent = name ? `Happy Birthday, ${name}!` : "Happy Birthday!";
}

function replayBloom() {
  flowerScene.classList.remove("is-playing");
  void flowerScene.offsetWidth;
  flowerScene.classList.add("is-playing");
}

nameInput.addEventListener("input", updateGreeting);
replayButton.addEventListener("click", replayBloom);

flowerScene.addEventListener("animationend", (event) => {
  if (event.animationName === "flower-arrive") {
    flowerScene.classList.remove("is-playing");
  }
});
