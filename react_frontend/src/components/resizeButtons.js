import React from "react";
import "../styles/liveFeedNavigation.css"
export default function ResizeButtons() {
    return (
        <>
        <div className="resize_buttons">
            <img src="/assets/plus.png" alt="plus-button" className="plus_btn"/>
            <img src="/assets/minus.png" alt="minus-button" className="minus_btn"/>
        </div>
        </>
    );
}