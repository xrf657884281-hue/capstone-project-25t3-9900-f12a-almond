import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "../ui/sheet"


const MobileNavigarion = () => {
  return (
    <Sheet>
        <SheetTrigger asChild>
            <img 
                src="hamburger.svg" 
                height={36}
                width={36}
                alt="menu"
                className="invert-colors sm:hidden"
            />
        </SheetTrigger>
        <SheetContent>
            <SheetHeader>
            <SheetTitle>Are you absolutely sure?</SheetTitle>
            <SheetDescription>
                This action cannot be undone. This will permanently delete your account
                and remove your data from our servers.
            </SheetDescription>
            </SheetHeader>
        </SheetContent>
    </Sheet>
  )
}

export default MobileNavigarion
