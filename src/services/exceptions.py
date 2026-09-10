class ErreurAlbert(Exception):
    pass


class ErreurRechercheDocuments(ErreurAlbert):
    pass


class ErreurCommunicationModele(ErreurAlbert):
    pass


class ErreurCommunicationModeleReformulation(ErreurCommunicationModele):
    pass


class ErreurCommunicationModeleReclassement(ErreurCommunicationModele):
    pass


class ErreurCommunicationModeleGeneration(ErreurCommunicationModele):
    pass


class ErreurCommunicationAlbert(ErreurAlbert):
    pass
