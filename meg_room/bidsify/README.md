

Automatic bidsification wrapper around mne_bids, for Neurospin meg plateform purpose



--> prend un projet depuis le serveur meg
--> renvoie les données bidsifiée sur un second serveur. 

Difficultés : 
--> gestion de l'extraction d'events (difficilement automatisable... quoi que si c'est bien fait depuis le début ça se fait)
--> prendre en compte la structure du projet (multi-session ou non ? [a discuter des particularités de chaque projet !...])



Plus généralement, il y a des outils puissants (mne_bids, mne_bids pipeline) mais qui demandent un peu de temps avant de bien être utilisé.
L'idée serait de faire un wrapper de plateforme d'acquisition pour ces outils, qui permettent d'automatiser la bidsficiation et le preprocessing 
côté ingénieur et que les chercheurs n'est plus à perdre du temps la-dedans.