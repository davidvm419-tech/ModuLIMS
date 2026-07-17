import type { Messages } from "../../interfaces/alerts";

export default function AlertMessages( { type, title, content }: Messages) {
    // boolean const
    const isSuccess = type === 'success';

    // create the classes if they are success or error
    const divClass = isSuccess ? 
    "bg-teal-100 border-teal-500 text-teal-900" :
    "bg-red-100 border-red-500 text-red-900";

    const iconClass = isSuccess ?
    "text-teal-500" :
    "text-red-500";

    return (
        <div className={`border-t-4 rounded-b px-4 py-3 shadow-md ${divClass}`} role="alert">
            <div className="flex justify-center items-center  gap-2">
                <div className="py-1"><svg className={`fill-current h-6 w-6 mr-4 ${iconClass}`} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                <path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zm12.73-1.41A8 8 0 1 0 4.34 4.34a8 8 0 0 0 11.32 11.32zM9 11V9h2v6H9v-4zm0-6h2v2H9V5z"/></svg></div>
                <div className="text-center">
                    <p className="font-bold">{title}</p>
                    <p className="text-sm">{content}</p>
                </div>
            </div>
        </div>    
    );
}