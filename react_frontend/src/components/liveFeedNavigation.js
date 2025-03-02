import "../styles/liveFeedNavigation.css"

export default function LiveFeedNavigation() {
    return (
        <>
        <div class="buttons">
            <button type="button" class="left"><img src="/assets/arrow.png" alt="right-arrow"/></button>
            <a href="/avatar-gallery" className="button"><img src="/assets/galleryicon.png" alt="gallery"/></a>
            <button type="button" class="right"><img src="/assets/arrow.png" alt="right-arrow" class="arrow"/></button>
        </div>
        </>
    );
  }