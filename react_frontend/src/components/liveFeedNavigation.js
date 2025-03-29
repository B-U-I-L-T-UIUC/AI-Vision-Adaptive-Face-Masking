import React from "react";
import NavigatingButtons from "./navigatingButtons";
import ResizeButtons from "./resizeButtons";
export default function LiveFeedNavigation() {
    return (
        <>
        <div className="all_buttons">
            <NavigatingButtons />
            <ResizeButtons />
        </div>
        </>
    );
}