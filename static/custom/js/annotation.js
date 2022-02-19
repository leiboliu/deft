class TaggingWord  {

    constructor(content_div) {
        this.currentTag = {};
        this.content_div = content_div;
        // content_div.mouseup(this.tagWord.bind(this));
        // console.log("created!");
    }

    setCurrentTag(tagName, tagColour) {
        this.currentTag = {tagName: tagName, tagColour: tagColour};
    }

    tagWord(env, username) {
        const initial_content_html = this.content_div.html();

        // expand to word. Disabled because some time need to tag the entity within a word. Like John's room. John will be the entity
        // snapSelectionToWord();

        var selection, selected_text, range_0;
        selection = document.getSelection();
        selected_text = selection.toString();
        // console.log('['+selected_text+']');
        if (selected_text.trim().length === 0 || selection.rangeCount === 0) return void(0);

        const selected_range = selection.getRangeAt(0);

        // remove extra whitespace
        const startOffset = selected_text.length - selected_text.trimStart().length;
        const endOffset = selected_text.length - selected_text.trimEnd().length;

        // console.log(selected_text.trimEnd());


        if (startOffset) {
            selected_range.setStart(selected_range.startContainer, selected_range.startOffset + startOffset);
        }

        if (endOffset) {
            selected_range.setEnd(selected_range.endContainer, selected_range.endOffset - endOffset);
        }

        selection.removeAllRanges();
        selection.addRange(selected_range);
        selected_text = selection.toString();

        // console.log(selection.anchorOffset);
        // console.log(selection.focusOffset);

        // if(Object.keys(this.currentTag).length === 0) {
        //     // alert('Please select a tag');
        //     showalert('Please select one entity category first!', 'alert-info');
        //     selection.empty();
        //     return void(0);
        // }

        // make sure the selection is within the given div
        // console.log('Anchor: ', selection.anchorNode.parentElement.id);
        // console.log('Focus: ', selection.focusNode.parentElement.id);
        // console.log('Content div: ', this.content_div[0].id);

        if (selection.anchorNode.parentElement.id != this.content_div[0].id ||
            selection.focusNode.parentElement.id != this.content_div[0].id) {
            selection.empty();
            return void(0);
        }

        // make sure the selected range with no span inside.
        for (var test_div = document.createElement("div"), c = 0, i = selection.rangeCount; c < i; ++c)
            test_div.appendChild(selection.getRangeAt(c).cloneContents());
        if (test_div.innerHTML.includes("<span class=")) return selection.empty();

        // Step 1: Get the range 0. Normally, only ONE range in a selection
        range_0 = selection.getRangeAt(0);

        // Step 2: Create the enclosure span
        var entity_span = document.createElement("span");
        var tooltip_msg = 'tagged by ' + username;
        entity_span.setAttribute('title', tooltip_msg);
        entity_span.className = "anno-entity";
        entity_span.style.borderColor = this.currentTag.tagColour;
        // need to add mouse click event: remove all
        // entity_span.onmouseup = this.deleteTag;

        // Step 3: Create span for Entity Word, the upper part, and append to enclosure span
        var word_span = document.createElement("span");
        word_span.className = "anno-words";
        word_span.style.color = this.currentTag.tagColour;
        word_span.appendChild(document.createTextNode(selected_text));
        entity_span.appendChild(word_span);

        // Step 4: Create span for NER Category, the lower part, and append to enclosure span
        var ner_span = document.createElement("span");
        ner_span.className = "anno-ner";
        ner_span.style.backgroundColor = this.currentTag.tagColour;
        ner_span.appendChild(document.createTextNode(this.currentTag.tagName));
        entity_span.appendChild(ner_span)

        // Step 5: replace contents of Range 0
        range_0.deleteContents()
        range_0.insertNode(entity_span)



        // step 6: smart research
        // const doc_content_text = $('#content-div').text();
        // var found = doc_content_text.toLowerCase().search(selected_text.toLowerCase());
        // while (found >=0 ) {
        //     selected_range.setStart(selected_range.startContainer, found);
        //     selected_range.setEnd(selected_range.endContainer, found + selected_text.length);
        //
        //     selected_range.deleteContents();
        //     selected_range.insertNode(entity_span);
        //     console.log('add span at ' + found);
        //     found = doc_content_html.toLowerCase().search(selected_text.toLowerCase());
        //
        // }

        // const doc_content_text = $('#content-div').html();
        // var selectedTextRegExp = new RegExp(selected_text, "gi");
        // console.log(selectedTextRegExp);
        // var replaced_text = doc_content_text.replace(selectedTextRegExp, '<span style="color:red">' + selected_text +'</span>');
        // $('#content-div').html(replaced_text);


        // Step 7: Deselect all
        selection.empty();

        // const tagged_entity_html = entity_span.outerHTML;
        var after_content_html = this.content_div.html();
        return get_selection_index(initial_content_html, after_content_html, selected_text,
            this.currentTag.tagName, this.currentTag.tagColour, username);
        // var first_difference_index = findFirstDiffPos(initial_content_html, after_content_html);
        // var tmp_div = document.createElement("div");
        // tmp_div.innerHTML = after_content_html.substring(0, first_difference_index);
        // //var before_entity_text = tmp_div.innerText;
        // var first_span_element = tmp_div.getElementsByClassName('anno-entity');
        // while (first_span_element.length > 0) {
        //     tmp_div.insertBefore(document.createTextNode(first_span_element[0].children[0].innerText), first_span_element[0]);
        //     tmp_div.removeChild(first_span_element[0]);
        //     console.log('remove 1 entity');
        //     first_span_element = tmp_div.getElementsByClassName('anno-entity');
        // }
        //
        // var new_entity_start = tmp_div.innerText.length;
        // var new_entity_end = new_entity_start + selected_text.length;
        // console.log('start ' + new_entity_start + ' end: ' + new_entity_end);
        // console.log('text:' + selected_text)
        // console.log('before_text:' + tmp_div.innerText);

        // tmp_div.innerHTML = after_content_html.substring(first_difference_index + tagged_entity_html.length);
        // var after_entity_text = tmp_div.innerText;
        // console.log('after_text:' + after_entity_text);

        // return {
        //     'start': new_entity_start,
        //     'end': new_entity_end,
        //     'text': selected_text,
        //     'entity': this.currentTag.tagName,
        //     'annotator': username,
        // }

    };

    deleteTag(e, username) {
        var target = e.target;
        if (target.getAttribute('class') == 'anno-ner' ||
            target.getAttribute('class') == 'anno-words') {
            target = target.parentNode;
        }

        var currentTag = target.children[1].innerHTML;
        var currentTag_color = target.children[1].style.backgroundColor;
        // console.log(target.children[1].style.backgroundColor);

        var parent = target.parentNode;
        if (!parent) {
            return
        }

        const initial_content_html = this.content_div.html();

        // console.log(target.children[0]);
        parent.insertBefore(document.createTextNode(target.children[0].innerHTML), target);
        parent.removeChild(target);
        e.stopPropagation();

        // get index
        var after_content_html = this.content_div.html();
        var selected_text = target.children[0].innerHTML;
        var entity_index = get_selection_index(initial_content_html, after_content_html, selected_text,
            currentTag, currentTag_color, username);

        // console.log(entity_index);
        return entity_index;
    }

    getHTML() {
        return this.content_div.html();
    };
}

function get_selection_index(initial_content_html, after_content_html, selected_text, tag_name, tag_color, username) {
        var first_difference_index = findFirstDiffPos(initial_content_html, after_content_html);
        var tmp_div = document.createElement("div");
        tmp_div.innerHTML = after_content_html.substring(0, first_difference_index);
        //var before_entity_text = tmp_div.innerText;
        var first_span_element = tmp_div.getElementsByClassName('anno-entity');
        while (first_span_element.length > 0) {
            tmp_div.insertBefore(document.createTextNode(first_span_element[0].children[0].innerText), first_span_element[0]);
            tmp_div.removeChild(first_span_element[0]);
            // console.log('remove 1 entity');
            first_span_element = tmp_div.getElementsByClassName('anno-entity');
        }

        var new_entity_start = tmp_div.innerText.length;
        var new_entity_end = new_entity_start + selected_text.length;
        // console.log('start ' + new_entity_start + ' end: ' + new_entity_end);
        // console.log('text:' + selected_text)
        // console.log('before_text:' + tmp_div.innerText);

        // tmp_div.innerHTML = after_content_html.substring(first_difference_index + tagged_entity_html.length);
        // var after_entity_text = tmp_div.innerText;
        // console.log('after_text:' + after_entity_text);

        return {
            'start': new_entity_start,
            'end': new_entity_end,
            'text': selected_text,
            'entity': tag_name,
            'entity_color': tag_color,
            'annotator': username,
        }
}

function set_colour(colour, name) {
    taggingWord.setCurrentTag(name, colour);

    if(c_tag_id) {
        let pt = document.getElementById(c_tag_id);
        // pt.classList.add("thin-btn");
        pt.classList.remove("rounded-pill");
        pt.classList.remove("border-dark");
        pt.classList.remove("border-3");
    }

    let ct = document.getElementById(name);
    // ct.classList.remove("thin-btn");
    ct.classList.add("rounded-pill");
    ct.classList.add("border-dark");
    ct.classList.add("border-3");

    c_tag_id = name;
}

function findFirstDiffPos(a, b)
{
   var shorterLength = Math.min(a.length, b.length);

   for (var i = 0; i < shorterLength; i++)
   {
       if (a[i] !== b[i]) return i;
   }

   if (a.length !== b.length) return shorterLength;

   return -1;
}

function snapSelectionToWord() {
    var sel;
    if (window.getSelection() && (sel = window.getSelection()).modify) {
        sel = window.getSelection();
        if (!sel.isCollapsed) {
            var range = document.createRange();
            range.setStart(sel.anchorNode, sel.anchorOffset);
            range.setEnd(sel.focusNode, sel.focusOffset);
            var backwards = range.collapsed;
            range.detach();

            var endNode = sel.focusNode, endOffset = sel.focusOffset;
            sel.collapse(sel.anchorNode, sel.anchorOffset);

            var direction = [];
            if (backwards) {
                direction = ['backward', 'forward'];
            } else {
                direction = ['forward', 'backward'];
            }
            sel.modify("move", direction[0], "character");
            sel.modify("move", direction[1], "word");
            sel.extend(endNode, endOffset);
            sel.modify("extend", direction[1], "character");
            sel.modify("extend", direction[0], "word");
        }
    } else if ((sel = document.selection) && sel.type != "Control") {
        var textRange = sel.createRange();
        if (textRange.text) {
            textRange.expand("word");
            while (/\s$/.test(textRange.text)) {
                textRange.moveEnd("character", -1);
            }
            textRange.select();
        }
    }
}