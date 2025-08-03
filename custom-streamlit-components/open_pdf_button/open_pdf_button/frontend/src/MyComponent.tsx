import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
  ReactElement,
} from "react"

/**
 * A template for creating Streamlit components with React
 *
 * This component demonstrates the essential structure and patterns for
 * creating interactive Streamlit components, including:
 * - Accessing props and args sent from Python
 * - Managing component state with React hooks
 * - Communicating back to Streamlit via Streamlit.setComponentValue()
 * - Using the Streamlit theme for styling
 * - Setting frame height for proper rendering
 *
 * @param {ComponentProps} props - The props object passed from Streamlit
 * @param {Object} props.args - Custom arguments passed from the Python side
 * @param {string} props.args.name - Example argument showing how to access Python-defined values
 * @param {boolean} props.disabled - Whether the component is in a disabled state
 * @param {Object} props.theme - Streamlit theme object for consistent styling
 * @returns {ReactElement} The rendered component
 */
function MyComponent({ args, disabled, theme }: ComponentProps): ReactElement {
  // Extract custom arguments passed from Python
  const { name } = args

  // Component state
  const [isFocused, setIsFocused] = useState(false)
  const [lastClickedLink, setLastClickedLink] = useState("Nothing clicked yet.");

  /**
   * Dynamic styling based on Streamlit theme and component state
   * This demonstrates how to use the Streamlit theme for consistent styling
   */
  const style: React.CSSProperties = useMemo(() => {
    if (!theme) return {}

    // Use the theme object to style the button border
    // Access theme properties like primaryColor, backgroundColor, etc.
    const borderStyling = `1px solid ${isFocused ? theme.primaryColor : "gray"}`
    return { border: borderStyling, outline: borderStyling }
  }, [theme, isFocused])

  /**
   * Tell Streamlit the height of this component
   * This ensures the component fits properly in the Streamlit app
   */
  useEffect(() => {
    // Call this when the component's size might change
    Streamlit.setFrameHeight()
    // Adding the style and theme as dependencies since they might
    // affect the visual size of the component.
  }, [style, theme])

  useEffect(() => {
    // This function will handle messages received from the parent (Streamlit app)
    const handleMessage = (event: MessageEvent) => {
      console.log("Received message from parent:", event);
      // It's good practice to check the origin for security
      // In production, you might want to be more specific.
      // console.log("Event source:", event.source);
      // console.log("Window.parent:", window.parent);
      // console.log("Should be true: ", window.parent === event.source);
      // if (event.source !== window.parent) return;

      const messageData = event.data;

      // Check if the message is the one we care about
      if (messageData.type === 'POPOVER_CLICKED') {
        const documentLink = messageData.documentLink;
        console.log(`React component received a click event for: ${documentLink}`);
        setLastClickedLink(documentLink);
        Streamlit.setComponentValue(documentLink);
      } else if (messageData.type === 'CLEAR_PDF') {
        // Handle the CLEAR_PDF message
        console.log("React component received a clear PDF event.");
        setLastClickedLink("Nothing clicked yet.");
        Streamlit.setComponentValue(null);
      }
    };

    // Add the event listener for 'message'
    window.addEventListener('message', handleMessage);

    // IMPORTANT: Return a cleanup function to remove the listener when the component unmounts
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, []); // The empty array ensures this effect runs only once


  return (
    <span>
      <h6>{name}</h6>
      <p>
        Document Link (popover only): <br/>{lastClickedLink}
      </p>
    </span>
  );
}

/**
 * withStreamlitConnection is a higher-order component (HOC) that:
 * 1. Establishes communication between this component and Streamlit
 * 2. Passes Streamlit's theme settings to your component
 * 3. Handles passing arguments from Python to your component
 * 4. Handles component re-renders when Python args change
 *
 * You don't need to modify this wrapper unless you need custom connection behavior.
 */
export default withStreamlitConnection(MyComponent)
