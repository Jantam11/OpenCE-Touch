/* Native platform gate for ChupathingyCE's unattended playlist host. */
#include "platform.h"
#include <stdlib.h>
BOOL platform_dedicated(void)
{
#ifdef HALO_ANDROID
	return FALSE;
#else
	const char *playlist = getenv("HALO_DEDICATED");
	return playlist && playlist[0];
#endif
}
