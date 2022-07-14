import './App.css';
import {CssVarsProvider, useColorScheme} from '@mui/joy/styles';
import {Grid, Container} from "@mui/material";
import Sheet from '@mui/joy/Sheet';
import Typography from '@mui/joy/Typography';
import Button from '@mui/joy/Button';

const MainSheetSX = {
    mx: 'auto', // margin left & right
    my: 4, // margin top & botom
    py: 3, // padding top & bottom
    px: 2, // padding left & right
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
    borderRadius: 'sm',
    boxShadow: 'md',
}

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
                        <Sheet sx={MainSheetSX}>
                            <Typography>Options</Typography>
                        </Sheet>

                    </Grid>
                    <Grid item xs={9}>
                        <Sheet sx={MainSheetSX}>
                            <Typography>Options</Typography>
                        </Sheet>
                    </Grid>
                </Grid>
            </Container>
        </CssVarsProvider>
    );
}

export default App;
