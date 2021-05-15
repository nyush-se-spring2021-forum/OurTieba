var query = window.location.search.substring(1);
var vars = query.split("&");

function getQueryVariable(variable) {
       for (let i=0;i<vars.length;i++) {
               let pair = vars[i].split("=");
               if(pair[0] === variable){
                   return pair[1];
               }
       }
       return false;
}

document.title = "OurTieba Player";

var s = getQueryVariable("src");
if (s.indexOf("/cdn/") !== 0) {
    s = "/cdn/" + s;
}
var a = getQueryVariable("autoplay");
var l = getQueryVariable("loop");

var autopause = autopause || true;

const dp = new DPlayer({
    container: document.getElementById('dplayer'),
    theme: '#FADFA3',
    lang: "en",
    mutex: true,
    autoplay: a,
    loop: l,
    contextmenu:[
        {
            text: autopause ? "Disable auto pause":"Enable auto pause",
            click: (player) => {
                let des = document.getElementsByClassName("dplayer-menu-item")[0].getElementsByTagName("a")[0];
                if (autopause) {
                    player.notice("Auto Pause OFF", 1000);
                    des.text = "Enable auto pause";
                    window.onblur = ()=>{};
                    window.onfocus = ()=>{};
                    autopause = false;
                } else  {
                    player.notice("Auto Pause ON", 1000);
                    des.text = "Disable auto pause";
                    window.onblur = function () {
                        player.pause();
                    }
                    window.onfocus = function () {
                        player.play();
                    }
                    autopause = true;
                }
            }
        }
    ],
    video: {
        url: s,
    },
})

//  display notice when in/out fullscreen mode
dp.on("fullscreen", () => {
    dp.notice("Enter Fullscreen", 1000);
})
dp.on("fullscreen_cancel", () => {
    dp.notice("Exit Fullscreen", 1000);
})

//  init autopause handlers
if (autopause) {
    window.onblur = function () {
        dp.pause();
    }
    window.onfocus = function () {
        dp.play();
    }
}