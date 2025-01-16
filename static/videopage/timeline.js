
let containerTime = document.getElementById("timeline");
let timelineWidth = 0;

var num_of_cells = 0;
function initializeTimeline() {
    let c = document.getElementById("scroll-mid").scrollWidth; // Get width of HTML page

    // Calculate the number of timeline cells required to cover the page width
    let numOfCells = Math.ceil(c / 75) + 1; // Add 1 to ensure it extends beyond 8

    for (let i = 0; i < numOfCells; i++) {
        let tdiv = document.createElement('div');
        tdiv.setAttribute('class', 'time-cell');

        let tsdiv = document.createElement('div');

        let tsp = document.createElement('p');
        tsp.setAttribute('class', 'time-num');

        if((timelineWidth / 75) % 2 == 0) {
            tsdiv.setAttribute('class', 'time-left-div');
            tsp.innerText = num_of_cells ++;
        }else
            tsdiv.setAttribute('class', 'time-left-div-bw');

         // Adjust the numbering

        containerTime.appendChild(tdiv);
        tdiv.appendChild(tsdiv);
        tdiv.appendChild(tsp);

        timelineWidth += 75;
    }
    document.getElementById("img_placeholder").style.width = document.getElementById('timeline').offsetWidth + "px";
    document.getElementById("audio_bar").style.width = document.getElementById('timeline').offsetWidth +"px";
    console.log(num_of_cells);
}

function adjustTimeline() {
    let c = document.getElementById('scroll-mid');
    let w = c.offsetWidth; // Get width of scroll-mid

    console.log(w);

    const sum1 = image_widths.reduce((total, current) => total + current, 0);
    const sum2 = audio_widths.reduce((total, current) => total + current, 0);
    let additionalContentWidth = Math.max(sum1, sum2);

    console.log(additionalContentWidth);
    // Calculate the required width of the timeline
    let requiredWidth = additionalContentWidth + 75; // Adjust as needed

    // Check if the required width is greater than the current width
    if (requiredWidth > timelineWidth) {
        // Calculate the number of timeline cells required
        let numOfCells = Math.ceil((requiredWidth - timelineWidth) / 75);

        for (let i = 0; i < numOfCells; i++) {
            let tdiv = document.createElement('div');
            tdiv.setAttribute('class', 'time-cell');

            let tsdiv = document.createElement('div');

            let tsp = document.createElement('p');
            tsp.setAttribute('class', 'time-num');

            if((timelineWidth / 75) % 2 == 0) {
                tsdiv.setAttribute('class', 'time-left-div');
                tsp.innerText = num_of_cells ++;
            }else
                tsdiv.setAttribute('class', 'time-left-div-bw');
            
            containerTime.appendChild(tdiv);
            tdiv.appendChild(tsdiv);
            tdiv.appendChild(tsp);

            timelineWidth += 75;
        }

        document.getElementById("img_placeholder").style.width = document.getElementById('timeline').offsetWidth + "px";
        document.getElementById("audio_bar").style.width = document.getElementById('timeline').offsetWidth +"px";
    }
}

// Initialize the timeline when the page loads
initializeTimeline();
