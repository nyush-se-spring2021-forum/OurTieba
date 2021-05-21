ue.ready(function () {
    // edui2(toolbar)
    $("#edui2").removeAttr("onselectstart onmousedown").on("selectstart", function () {
        return false;
    })
        .on("mousedown", function () {
            return $EDITORUI['edui2']._onMouseDown(event, this);
        })
    // edui3(emotion)
    $("#edui3_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
        return $EDITORUI['edui3'].Stateful_onMouseDown(event, this);
    }).on("mouseup", function () {
        return $EDITORUI['edui3'].Stateful_onMouseUp(event, this);
    }).on("mouseover", function () {
        return $EDITORUI['edui3'].Stateful_onMouseOver(event, this);
    }).on("mouseout", function () {
        return $EDITORUI['edui3'].Stateful_onMouseOut(event, this);
    })
    $("#edui3_button_body").removeAttr("onclick").on("click", function () {
        return $EDITORUI['edui3']._onButtonClick(event, this);
    })
    $(".edui-arrow").removeAttr("onclick").on("click", function () {
        return $EDITORUI['edui3']._onArrowClick(event, this);
    })
    // edui5(img)
    $("#edui5_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
        return $EDITORUI['edui5'].Stateful_onMouseDown(event, this);
    }).on("mouseup", function () {
        return $EDITORUI['edui5'].Stateful_onMouseUp(event, this);
    }).on("mouseover", function () {
        return $EDITORUI['edui5'].Stateful_onMouseOver(event, this);
    }).on("mouseout", function () {
        return $EDITORUI['edui5'].Stateful_onMouseOut(event, this);
    })
    $("#edui5_body").removeAttr("onclick onmousedown").on("click", function () {
        return $EDITORUI['edui5']._onButtonClick(event, this);
    })

    // edui12(multi_img)
    $("#edui12_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
        return $EDITORUI['edui12'].Stateful_onMouseDown(event, this);
    }).on("mouseup", function () {
        return $EDITORUI['edui12'].Stateful_onMouseUp(event, this);
    }).on("mouseover", function () {
        return $EDITORUI['edui12'].Stateful_onMouseOver(event, this);
    }).on("mouseout", function () {
        return $EDITORUI['edui12'].Stateful_onMouseOut(event, this);
    })
    $("#edui12_body").removeAttr("onclick onmousedown").on("click", function () {
        $EDITORUI['edui12']._onClick(event, this);
        // edui9("x")
        $("#edui9_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
            return $EDITORUI['edui9'].Stateful_onMouseDown(event, this);
        }).on("mouseup", function () {
            return $EDITORUI['edui9'].Stateful_onMouseUp(event, this);
        }).on("mouseover", function () {
            return $EDITORUI['edui9'].Stateful_onMouseOver(event, this);
        }).on("mouseout", function () {
            return $EDITORUI['edui9'].Stateful_onMouseOut(event, this);
        })
        $("#edui9_body").removeAttr("onclick onmousedown").on("click", function () {
            return $EDITORUI['edui9']._onClick(event, this);
        })
        // edui10("OK")
        $("#edui10_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
            return $EDITORUI['edui10'].Stateful_onMouseDown(event, this);
        }).on("mouseup", function () {
            return $EDITORUI['edui10'].Stateful_onMouseUp(event, this);
        }).on("mouseover", function () {
            return $EDITORUI['edui10'].Stateful_onMouseOver(event, this);
        }).on("mouseout", function () {
            return $EDITORUI['edui10'].Stateful_onMouseOut(event, this);
        })
        $("#edui10_body").removeAttr("onclick onmousedown").on("click", function () {
            return $EDITORUI['edui10']._onClick(event, this);
        })
        // edui11("Cancel")
        $("#edui11_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
            return $EDITORUI['edui11'].Stateful_onMouseDown(event, this);
        }).on("mouseup", function () {
            return $EDITORUI['edui11'].Stateful_onMouseUp(event, this);
        }).on("mouseover", function () {
            return $EDITORUI['edui11'].Stateful_onMouseOver(event, this);
        }).on("mouseout", function () {
            return $EDITORUI['edui11'].Stateful_onMouseOut(event, this);
        })
        $("#edui11_body").removeAttr("onclick onmousedown").on("click", function () {
            return $EDITORUI['edui11']._onClick(event, this);
        })
    })

    // edui17(video)
    $("#edui17_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
        return $EDITORUI['edui17'].Stateful_onMouseDown(event, this);
    }).on("mouseup", function () {
        return $EDITORUI['edui17'].Stateful_onMouseUp(event, this);
    }).on("mouseover", function () {
        return $EDITORUI['edui17'].Stateful_onMouseOver(event, this);
    }).on("mouseout", function () {
        return $EDITORUI['edui17'].Stateful_onMouseOut(event, this);
    })
    $("#edui17_body").removeAttr("onclick onmousedown").on("click", function () {
        $EDITORUI['edui17']._onClick(event, this);
        // edui14("x")
        $("#edui14_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
            return $EDITORUI['edui14'].Stateful_onMouseDown(event, this);
        }).on("mouseup", function () {
            return $EDITORUI['edui14'].Stateful_onMouseUp(event, this);
        }).on("mouseover", function () {
            return $EDITORUI['edui14'].Stateful_onMouseOver(event, this);
        }).on("mouseout", function () {
            return $EDITORUI['edui14'].Stateful_onMouseOut(event, this);
        })
        $("#edui14_body").removeAttr("onclick onmousedown").on("click", function () {
            return $EDITORUI['edui14']._onClick(event, this);
        })
        // edui15("OK")
        $("#edui15_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
            return $EDITORUI['edui15'].Stateful_onMouseDown(event, this);
        }).on("mouseup", function () {
            return $EDITORUI['edui15'].Stateful_onMouseUp(event, this);
        }).on("mouseover", function () {
            return $EDITORUI['edui15'].Stateful_onMouseOver(event, this);
        }).on("mouseout", function () {
            return $EDITORUI['edui15'].Stateful_onMouseOut(event, this);
        })
        $("#edui15_body").removeAttr("onclick onmousedown").on("click", function () {
            return $EDITORUI['edui15']._onClick(event, this);
        })
        // edui16("Cancel")
        $("#edui16_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
            return $EDITORUI['edui16'].Stateful_onMouseDown(event, this);
        }).on("mouseup", function () {
            return $EDITORUI['edui16'].Stateful_onMouseUp(event, this);
        }).on("mouseover", function () {
            return $EDITORUI['edui16'].Stateful_onMouseOver(event, this);
        }).on("mouseout", function () {
            return $EDITORUI['edui16'].Stateful_onMouseOut(event, this);
        })
        $("#edui16_body").removeAttr("onclick onmousedown").on("click", function () {
            return $EDITORUI['edui16']._onClick(event, this);
        })
    })

    // edui22(link)
    $("#edui22_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
        return $EDITORUI['edui22'].Stateful_onMouseDown(event, this);
    }).on("mouseup", function () {
        return $EDITORUI['edui22'].Stateful_onMouseUp(event, this);
    }).on("mouseover", function () {
        return $EDITORUI['edui22'].Stateful_onMouseOver(event, this);
    }).on("mouseout", function () {
        return $EDITORUI['edui22'].Stateful_onMouseOut(event, this);
    })
    $("#edui22_body").removeAttr("onclick onmousedown").on("click", function () {
        $EDITORUI['edui22']._onClick(event, this);
        // edui19("x")
        $("#edui19_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
            return $EDITORUI['edui19'].Stateful_onMouseDown(event, this);
        }).on("mouseup", function () {
            return $EDITORUI['edui19'].Stateful_onMouseUp(event, this);
        }).on("mouseover", function () {
            return $EDITORUI['edui19'].Stateful_onMouseOver(event, this);
        }).on("mouseout", function () {
            return $EDITORUI['edui19'].Stateful_onMouseOut(event, this);
        })
        $("#edui19_body").removeAttr("onclick onmousedown").on("click", function () {
            return $EDITORUI['edui19']._onClick(event, this);
        })
        // edui20("OK")
        $("#edui20_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
            return $EDITORUI['edui20'].Stateful_onMouseDown(event, this);
        }).on("mouseup", function () {
            return $EDITORUI['edui20'].Stateful_onMouseUp(event, this);
        }).on("mouseover", function () {
            return $EDITORUI['edui20'].Stateful_onMouseOver(event, this);
        }).on("mouseout", function () {
            return $EDITORUI['edui20'].Stateful_onMouseOut(event, this);
        })
        $("#edui20_body").removeAttr("onclick onmousedown").on("click", function () {
            return $EDITORUI['edui20']._onClick(event, this);
        })
        // edui21("Cancel")
        $("#edui21_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
            return $EDITORUI['edui21'].Stateful_onMouseDown(event, this);
        }).on("mouseup", function () {
            return $EDITORUI['edui21'].Stateful_onMouseUp(event, this);
        }).on("mouseover", function () {
            return $EDITORUI['edui21'].Stateful_onMouseOver(event, this);
        }).on("mouseout", function () {
            return $EDITORUI['edui21'].Stateful_onMouseOut(event, this);
        })
        $("#edui21_body").removeAttr("onclick onmousedown").on("click", function () {
            return $EDITORUI['edui21']._onClick(event, this);
        })
    })

    // edui24(undo)
    $("#edui24_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
        return $EDITORUI['edui24'].Stateful_onMouseDown(event, this);
    }).on("mouseup", function () {
        return $EDITORUI['edui24'].Stateful_onMouseUp(event, this);
    }).on("mouseover", function () {
        return $EDITORUI['edui24'].Stateful_onMouseOver(event, this);
    }).on("mouseout", function () {
        return $EDITORUI['edui24'].Stateful_onMouseOut(event, this);
    })
    $("#edui24_body").removeAttr("onclick onmousedown").on("click", function () {
        return $EDITORUI['edui24']._onClick(event, this);
    })

    // edui25(redo)
    $("#edui25_state").removeAttr("onmousedown onmouseup onmouseover onmouseout").on("mousedown", function () {
        return $EDITORUI['edui25'].Stateful_onMouseDown(event, this);
    }).on("mouseup", function () {
        return $EDITORUI['edui25'].Stateful_onMouseUp(event, this);
    }).on("mouseover", function () {
        return $EDITORUI['edui25'].Stateful_onMouseOver(event, this);
    }).on("mouseout", function () {
        return $EDITORUI['edui25'].Stateful_onMouseOut(event, this);
    })
    $("#edui25_body").removeAttr("onclick onmousedown").on("click", function () {
        return $EDITORUI['edui25']._onClick(event, this);
    })
})