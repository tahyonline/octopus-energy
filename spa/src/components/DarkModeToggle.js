import {useColorScheme} from "@mui/joy/styles";
import Button from "@mui/joy/Button";

function DarkModeToggle() {
  const { mode, setMode } = useColorScheme();
  return (
    <Button
      variant="outlined"
      color="neutral"
      onClick={() => setMode(mode === 'dark' ? 'light' : 'dark')}
    >
      {mode === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
    </Button>
  );
}

export default DarkModeToggle;