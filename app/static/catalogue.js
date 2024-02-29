filter_menu = document.getElementById("filter_menu")
searchbar = document.getElementById("searchbar")
pph_min = document.getElementById("pph_min")
pph_max = document.getElementById("pph_max")
lecturers = document.getElementById("lecturers")
       
filter_menu.style.setProperty("display", "none", "important")
filter_menu_visible = false

function on_filter_btn_clicked() {
    filter_menu_visible = !filter_menu_visible
    if (filter_menu_visible) {
        filter_menu.style.removeProperty("display")
        return
    }
    filter_menu.style.setProperty("display", "none", "important")
}

function on_search() {
    console.log("Query: ", searchbar.value)
    console.log("Min: ", parseInt(pph_min.value))
    console.log("Max: ", parseInt(pph_max.value))

    for (let lecturer of lecturers.children) {
        name = lecturer.children[0].children[1].children[0].children[0].innerHTML
	lecturer_pph = {"innerHtml": "-1"}
	for (let lp of lecturer.children[0].children[1].children) {
	    if (lp.className.includes("lecturer-pph")) {
		lecturer_pph = lp.children[1]
		break;
	    }	
	}
	pph = parseInt(lecturer_pph.innerHTML)

	console.log("Lecturer PPH: ", pph)
        nameMatch = name.toLowerCase().includes(searchbar.value.toLowerCase())
	let min_pph = -1
	let max_pph = -1
	if (!pph_min.value.length < 1) {
	    min_pph = parseInt(pph_min.value)
	}
	if (!pph_max.value.length < 1) {
	    max_pph = parseInt(pph_max.value)
	}
	let priceMatch = false
	if (!(pph < min_pph || pph > max_pph)) {
	    priceMatch = true
	}
	if (pph == -1 || (min_pph == -1 && pph <= max_pph) || (max_pph == -1 && pph >= min_pph)) {
	    priceMatch = true
	}

	lecturer_location = {"innerText": "*"}
	for (let lp of lecturer.children[0].children[1].children) {
	    if (lp.className.includes("lecturer-location")) {
		lecturer_location = lp.children[1]
		break;
	    }	
	}

	wanted_locations = []
	location_toggles = document.getElementsByClassName("location-toggle")
	for (let loc_tog of location_toggles) {
	    l = loc_tog.children[1].innerText
	    if (!loc_tog.children[0].checked) {
	    	wanted_locations = wanted_locations.concat([l])
	    }
	}

	if (wanted_locations.includes(lecturer_location.innerText) || lecturer_location.innerText == "*") {
	    locationMatch = true
	} else {
	    locationMatch = false
	}

	lecturer_tags = []
	for (let tag_span of lecturer.children[2].children[1].children) {
	    lecturer_tags = lecturer_tags.concat([tag_span.innerText])
	}

	required_tags = []
	tag_toggles = document.getElementsByClassName("tag-toggle")
	for (let tag_tog of tag_toggles) {
	    l = tag_tog.children[1].innerText
	    if (tag_tog.children[0].checked) {
	    	required_tags = required_tags.concat([l])
	    }
	}
	
	tagMatch = lecturer_tags.includes(required_tags) || required_tags.length == 0

	if (nameMatch && priceMatch && locationMatch && tagMatch) {
	   lecturer.style.removeProperty("display")
	} else {
           lecturer.style.setProperty("display", "none", "important")
	}
    }
}

