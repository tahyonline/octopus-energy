import './App.css';
import {CssVarsProvider, useColorScheme} from '@mui/joy/styles';
import {Grid, Container} from "@mui/material";
import Sheet from '@mui/joy/Sheet';
import Typography from '@mui/joy/Typography';
import Button from '@mui/joy/Button';


function App() {
    fetch('/hello')
      .then(response => response.json())
      .then(data => console.log(data));
    fetch('/hello2')
      .then(response => response.json())
      .then(data => console.log(data));
    return (
        <CssVarsProvider>
            <Container>
                <Grid container spacing={2}>
                    <Grid item xs={3}>
                        <Typography>Options</Typography>
                    </Grid>
                    <Grid item xs={9}>
                        <Typography>Content</Typography>
                    </Grid>
                </Grid>
            </Container>
        </CssVarsProvider>
    );
}

export default App;
