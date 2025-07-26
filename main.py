import logging
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Error


# --- Selectors ---
COOKIES_BUTTON = "button:has-text('Allow all cookies')"
USERNAME_INPUT = "input[name='username']"
PASSWORD_INPUT = "input[name='password']"
DIRECT_INBOX_ICON = "[aria-label='Direct']"
NOTIFICATIONS_BUTTON = "button:has-text('Not now')"
CONVERSATION_LIST_ITEM = "[role='presentation']"
CONVERSATION_LINK = '[role="link"][href][aria-label^="Open the profile page of "]'
GROUP_CHAT_HEADER = '[role="button"][aria-label="Open the details pane of the chat"]'
CONVERSATION_HEADER = '[aria-label^="Conversation with"]'
USER_AVATAR = "[alt='User avatar']"
MESSAGE_LIKE_BUTTON = "[aria-label='Double tap to like']"
MESSAGE_OPTIONS_BUTTON = '[aria-label^="See more options "]'
UNSEND_BUTTON = "[aria-label='Unsend']"
CONFIRM_UNSEND_BUTTON = 'button:has-text("Unsend")'


def setup_logging():
    """Configures logging to output to both file and console."""
    log_filename = f"cleansta_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # File Handler
    file_handler = logging.FileHandler(log_filename, mode="w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def login(page: Page):
    """Waits for the user to manually log into Instagram."""
    logging.info("Waiting for manual login...")
    input(
        "Veuillez vous connecter à Instagram dans le navigateur ouvert, puis appuyez sur Entrée pour continuer..."
    )
    page.wait_for_selector(DIRECT_INBOX_ICON, timeout=120000)  # Wait 2 minutes
    logging.info("Login confirmed by user.")


def delete_visible_outgoing_messages(page: Page) -> bool:
    """Finds and deletes all visible outgoing messages."""
    all_messages = page.query_selector_all(MESSAGE_LIKE_BUTTON)
    outgoing_messages = []
    for msg in all_messages:
        parent = msg.query_selector("..")
        if parent:
            sibling = parent.query_selector("xpath=preceding-sibling::*[1]")
            if sibling:
                style = sibling.get_attribute("style")
                if style and "--paddingInlineStart" in style:
                    outgoing_messages.append(msg)

    if not outgoing_messages:
        logging.info("No visible outgoing messages to delete in this view.")
        return False

    logging.info(f"Found {len(outgoing_messages)} outgoing messages to delete.")
    for message in reversed(outgoing_messages):
        try:
            content = message.inner_text().strip()
            logging.info(f"   Removing message: {content}")

            message.scroll_into_view_if_needed()
            message.hover()

            page.wait_for_selector(MESSAGE_OPTIONS_BUTTON, timeout=1000)
            page.click(MESSAGE_OPTIONS_BUTTON)

            page.wait_for_selector(UNSEND_BUTTON, timeout=1000)
            page.click(UNSEND_BUTTON)

            page.wait_for_selector(CONFIRM_UNSEND_BUTTON, timeout=1000)
            page.click(CONFIRM_UNSEND_BUTTON)

            page.wait_for_timeout(1000)  # Wait for the unsend action to complete

            logging.info("   Message unsent.")
        except Error as e:
            logging.error(f"Failed to delete a message: {e}")
            page.keyboard.press("Escape")  # Try to recover by closing menus
            continue
    return True


def clean_conversation(page: Page):
    """Scrolls up and deletes all outgoing messages until the conversation header is visible."""
    logging.info("Starting to clean conversation...")
    page.wait_for_selector(f"{CONVERSATION_LINK}, {GROUP_CHAT_HEADER}", timeout=10000)

    # Log conversation name
    dest = page.query_selector(CONVERSATION_LINK) or page.query_selector(
        GROUP_CHAT_HEADER
    )
    if dest:
        logging.info("- Cleaning: %s", " ".join(dest.inner_text().split("\n")))

    # Main loop to scroll and delete
    conv = page.query_selector(CONVERSATION_HEADER)
    if conv and conv.is_visible():
        while True:
            delete_visible_outgoing_messages(page)

            header = conv.query_selector(USER_AVATAR)
            if header and header.is_visible():
                logging.info("Conversation header is visible. Finishing up.")
                break

            conv.click()
            logging.info("Scrolling up...")
            page.keyboard.press("Home")

    # Final cleanup pass at the top
    logging.info("Finished cleaning conversation.")


def process_conversations(page: Page):
    """Iterates through all conversations and cleans them."""
    logging.info("Navigating to Direct Inbox...")
    if not page.url.startswith("https://www.instagram.com/direct/inbox/"):
        page.goto("https://www.instagram.com/direct/inbox/")

    logging.info("Retrieving list of conversation names...")
    page.wait_for_selector(CONVERSATION_LIST_ITEM)
    initial_conversations = page.query_selector_all(CONVERSATION_LIST_ITEM)

    conversation_names = []
    # Skip the first item which is usually "Notes"
    for conv in initial_conversations[1:]:
        try:
            # Extract the first line of text as the identifier
            name = conv.inner_text().split("\n")[0]
            if name:
                conversation_names.append(name)
        except Exception as e:
            logging.warning(f"Could not extract name from a conversation: {e}")

    logging.info(
        f"Found {len(conversation_names)} conversations to process: {conversation_names}"
    )

    for name in conversation_names:
        try:
            logging.info(f"--- Processing conversation: {name} ---")
            # Find the conversation by its name on the current page
            # Using a text selector is more robust than relying on element order
            page.wait_for_selector(f":text-is('{name}')")
            conv_element = page.query_selector(f":text-is('{name}')")

            if not conv_element:
                logging.warning(f"Could not find conversation for '{name}'. Skipping.")
                continue

            # The clickable element is a parent of the text element
            parent_button = conv_element.query_selector(
                "xpath=ancestor-or-self::div[@role='button']"
            )
            if parent_button:
                parent_button.click()
                clean_conversation(page)
                logging.info("Returning to conversation list.")
                page.go_back()
                page.wait_for_selector(CONVERSATION_LIST_ITEM)  # Wait for inbox to load
            else:
                logging.warning(
                    f"Could not find clickable parent for conversation '{name}'."
                )

        except Error as e:
            logging.error(f"Failed to process conversation '{name}': {e}")
            # Go back to the inbox to try the next one
            if "direct/inbox" not in page.url:
                page.goto("https://www.instagram.com/direct/inbox/")
            continue


def main():
    """Main function to run the Instagram cleaning script."""
    setup_logging()
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="./user_data", headless=False
        )
        page = browser.pages[0]

        try:
            page.goto("https://www.instagram.com/")
            logging.info("Navigated to Instagram.")
            login(page)
            process_conversations(page)

        except Error as e:
            logging.error(f"A critical error occurred: {e}")
        finally:
            logging.info("End of session.")
            # browser.close()


if __name__ == "__main__":
    main()
