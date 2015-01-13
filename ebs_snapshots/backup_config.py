class BackupConfig:
    """
    Interface shared by backup configs  

    Config items are dicts, with key equal to the volume id mapped to a dict of 
    parameters

    {
        "vol-1234567" : {
            "interval": "daily",
            "max_snapshots": 7,
            ...
        },
        ...
    }
    """
    pass
