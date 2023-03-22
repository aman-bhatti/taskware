$(document).ready(function () {
    let streakCounter = 1;
    $("#streak-counter").text(streakCounter.toString());

    $("#minus-btn").click(function () {
        if (streakCounter > 1) {
            streakCounter = streakCounter - 1;
            $("#streak-counter").text(streakCounter.toString());
        }
    });
    $("#plus-btn").click(function () {
        if (streakCounter < 10) {
            streakCounter = streakCounter + 1;
            $("#streak-counter").text(streakCounter.toString());
        }
    });

    var links = document.getElementsByClassName("nav-link");
    for (var i = 0; i < links.length; i++) {
        links[i].addEventListener("click", function () {
            var current = document.getElementsByClassName("nav-active");
            current[0].className = current[0].className.replace(" nav-active", "");
            this.className += " nav-active";
        });
    }

    let sidebars = document.getElementsByClassName('aside-item');
    for (var i = 0; i < sidebars.length; i++) {
        sidebars[i].addEventListener("click", function () {
            var current = document.getElementsByClassName("aside-active");
            current[0].className = current[0].className.replace(" aside-active", "");
            this.className += " aside-active";
        });
    }

    let tabBars = document.getElementsByClassName('tab-item');
    for (var i = 0; i < tabBars.length; i++) {
        tabBars[i].addEventListener("click", function () {
            var current = document.getElementsByClassName("tab-active");
            current[0].className = current[0].className.replace(" tab-active", "");
            this.className += " tab-active";
        });
    }


});