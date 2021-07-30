const buttons = document.getElementsByClassName("dropdown-button")
for(let i=0;i<buttons.length;i++) {
    $(buttons[i]).click(()=>{
    $(buttons[i]).next().toggle();
    })
}