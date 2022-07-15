import './App.css';
import {useState} from "react";
import {CssVarsProvider} from '@mui/joy/styles';
import {Grid, Container} from "@mui/material";
import Sheet from '@mui/joy/Sheet';
import Button from '@mui/joy/Button';

import DarkModeToggle from "./components/DarkModeToggle";

import AcquisitionPane from "./components/AcquisitionPane";
import DailyConsumption from "./components/DailyConsumption";
import RunningAverages from "./components/RunningAverages";
const selectablePanes = {
    data: {
        title: "Data Acquisition",
        pane: <AcquisitionPane/>,
    },
    daily: {
        title: "Daily Consumption",
        pane: <DailyConsumption/>,
    },
    avg: {
        title: "Running Averages",
        pane: <RunningAverages/>,
    }
}

const MainSheetSX = {
    mx: 'auto',
    my: 4,
    py: 3,
    px: 2,
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
    borderRadius: 'sm',
    boxShadow: 'md',
};

function App() {
    let [selectedPane, setSelectedPane] = useState("data");

    return (
        <CssVarsProvider>
            <Container>
                <Grid container spacing={2}>
                    <Grid item xs={3}>
                        <Sheet sx={MainSheetSX}>
                            {
                                Object.keys(selectablePanes).map((id) => (
                                    <Button
                                        variant="soft"
                                        onClick={() => setSelectedPane(id)}
                                        disabled={selectedPane === id}
                                        color="info"
                                        key={"pane-selector-" + id}
                                    >{selectablePanes[id].title}</Button>
                                ))
                            }
                            <DarkModeToggle/>
                        </Sheet>
                    </Grid>
                    <Grid item xs={9} minWidth="200px">
                        <Sheet sx={MainSheetSX}>
                            {selectablePanes[selectedPane].pane}
                        </Sheet>
                    </Grid>
                </Grid>
            </Container>
        </CssVarsProvider>
    );
}

export default App;
